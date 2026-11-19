import html
import logging
import re
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import AGE_RANGES, settings
from database import TZ, Database
from keyboards import age_kb, language_kb, main_menu, phone_kb, yes_no_kb
from states import Survey
from texts import CHOOSE_LANGUAGE, LANGUAGES, t

logger = logging.getLogger(__name__)
router = Router()


async def _drop_inline_kb(call: CallbackQuery) -> None:
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramAPIError:
        pass


# ---- Шаг 1: язык ----------------------------------------------------------
@router.callback_query(Survey.language, F.data.startswith("lang:"))
async def choose_language(call: CallbackQuery, state: FSMContext, db: Database):
    lang = call.data.split(":", 1)[1]
    if lang not in LANGUAGES:
        await call.answer()
        return
    data = await state.get_data()
    await db.upsert_user(
        call.from_user.id, call.from_user.username, lang, data.get("source")
    )
    await state.update_data(language=lang)
    await state.set_state(Survey.name)
    await _drop_inline_kb(call)
    await call.message.answer(t(lang, "ask_name"))
    await call.answer()


# ---- Шаг 2: имя -----------------------------------------------------------
@router.message(Survey.name, F.text)
async def got_name(message: Message, state: FSMContext):
    lang = (await state.get_data())["language"]
    name = message.text.strip()
    if name.startswith("/") or not 2 <= len(name) <= 64:
        await message.answer(t(lang, "invalid_name"))
        return
    await state.update_data(name=name)
    await state.set_state(Survey.seller)
    await message.answer(t(lang, "ask_seller"), reply_markup=yes_no_kb(lang))


# ---- Шаг 3: продавец? -----------------------------------------------------
@router.callback_query(Survey.seller, F.data.in_({"seller:yes", "seller:no"}))
async def got_seller(call: CallbackQuery, state: FSMContext):
    lang = (await state.get_data())["language"]
    await state.update_data(is_uzum_seller=call.data == "seller:yes")
    await state.set_state(Survey.age)
    await _drop_inline_kb(call)
    await call.message.answer(t(lang, "ask_age"), reply_markup=age_kb())
    await call.answer()


# ---- Шаг 4: возраст -------------------------------------------------------
@router.callback_query(Survey.age, F.data.startswith("age:"))
async def got_age(call: CallbackQuery, state: FSMContext):
    age = call.data.split(":", 1)[1]
    if age not in AGE_RANGES:
        await call.answer()
        return
    lang = (await state.get_data())["language"]
    await state.update_data(age_range=age)
    await state.set_state(Survey.phone)
    await _drop_inline_kb(call)
    await call.message.answer(t(lang, "ask_phone"), reply_markup=phone_kb(lang))
    await call.answer()


# ---- Шаг 5: телефон -------------------------------------------------------
def normalize_phone(raw: str) -> str | None:
    """Базовая валидация: 9 цифр -> +998XXXXXXXXX, 10–15 цифр -> +<цифры>."""
    if not re.fullmatch(r"[\d\s()+\-]+", raw):
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 9:
        return "+998" + digits
    if 10 <= len(digits) <= 15:
        return "+" + digits
    return None


@router.message(Survey.phone, F.contact)
async def got_contact(message: Message, state: FSMContext, bot: Bot, db: Database):
    lang = (await state.get_data())["language"]
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer(t(lang, "invalid_contact"), reply_markup=phone_kb(lang))
        return
    phone = normalize_phone(contact.phone_number) or contact.phone_number
    await finish_survey(message, state, bot, db, phone)


@router.message(Survey.phone, F.text)
async def got_phone_text(message: Message, state: FSMContext, bot: Bot, db: Database):
    lang = (await state.get_data())["language"]
    phone = normalize_phone(message.text.strip())
    if not phone:
        await message.answer(t(lang, "invalid_phone"), reply_markup=phone_kb(lang))
        return
    await finish_survey(message, state, bot, db, phone)


async def finish_survey(
    message: Message, state: FSMContext, bot: Bot, db: Database, phone: str
):
    data = await state.get_data()
    lang = data["language"]
    user = message.from_user
    await db.complete_survey(
        user.id,
        user.username,
        data["name"],
        data["is_uzum_seller"],
        data["age_range"],
        phone,
    )
    await state.clear()
    # Главное меню заменяет клавиатуру с запросом контакта (она исчезает).
    await message.answer(t(lang, "survey_done"), reply_markup=main_menu(lang))
    await notify_admin(bot, db, user.id)


async def notify_admin(bot: Bot, db: Database, user_id: int) -> None:
    u = await db.get_user(user_id)
    if not u:
        return
    esc = html.escape
    profile = f'<a href="tg://user?id={u["user_id"]}">открыть профиль</a>'
    username = f"@{esc(u['username'])} ({profile})" if u["username"] else profile
    created = datetime.fromisoformat(u["created_at"]).astimezone(TZ)
    text = (
        "🆕 <b>Новая заявка</b>\n\n"
        f"👤 Имя: {esc(u['name'])}\n"
        f"🔗 Telegram: {username}\n"
        f"🆔 ID: <code>{u['user_id']}</code>\n"
        f"🌐 Язык: {LANGUAGES.get(u['language'], u['language'])}\n"
        f"🛒 Продавец на Uzum: {'Да' if u['is_uzum_seller'] else 'Нет'}\n"
        f"🎂 Возраст: {esc(u['age_range'])}\n"
        f"📱 Телефон: {esc(u['phone'])}\n"
        f"📍 Источник: {esc(u['source']) if u['source'] else 'direct (без метки)'}\n"
        f"🕒 Дата: {created:%d.%m.%Y %H:%M}"
    )
    try:
        await bot.send_message(settings.ADMIN_ID, text)
    except TelegramAPIError as e:
        # Админ должен хотя бы раз нажать /start у бота, иначе Telegram не даст написать.
        logger.error("Не удалось отправить заявку админу: %s", e)


# ---- Подстраховки ---------------------------------------------------------
@router.message(StateFilter(Survey.language))
async def language_fallback(message: Message):
    await message.answer(CHOOSE_LANGUAGE, reply_markup=language_kb())


@router.message(StateFilter(Survey.seller, Survey.age))
async def buttons_fallback(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language")
    await message.answer(t(lang, "use_buttons"))


@router.message(StateFilter(Survey.name))
async def name_fallback(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language")
    await message.answer(t(lang, "invalid_name"))


@router.message(StateFilter(Survey.phone))
async def phone_fallback(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("language")
    await message.answer(t(lang, "invalid_phone"), reply_markup=phone_kb(lang))


@router.callback_query(F.data.startswith(("lang:", "seller:", "age:")))
async def stale_callback(call: CallbackQuery):
    await call.answer()
