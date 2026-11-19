import logging

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import BUTTON_TO_PRODUCT, PRODUCTS, get_product_file, settings
from database import Database
from keyboards import main_menu, subscribe_kb
from texts import NOT_REGISTERED, t

logger = logging.getLogger(__name__)
router = Router()

MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def is_member(bot: Bot, user_id: int) -> bool | None:
    """True/False — состоит ли в группе; None — не удалось проверить (ошибка API)."""
    try:
        m = await bot.get_chat_member(chat_id=settings.TARGET_GROUP_ID, user_id=user_id)
    except TelegramAPIError as e:
        logger.error(
            "get_chat_member failed (бот добавлен в группу админом? верный ли ID?): %s", e
        )
        return None
    if m.status in MEMBER_STATUSES:
        return True
    # «ограниченный» участник всё ещё находится в группе
    return m.status == ChatMemberStatus.RESTRICTED and bool(getattr(m, "is_member", False))


async def send_product(bot: Bot, chat_id: int, lang: str, product_id: str) -> None:
    product = PRODUCTS[product_id]
    text = product["text"][lang]
    if product.get("link"):
        text += f"\n\n🔗 {product['link']}"

    path = get_product_file(product_id, lang)
    if path and path.is_file():
        await bot.send_document(chat_id, FSInputFile(path), caption=text)
    else:
        if path:
            logger.warning("Файл %s не найден в materials/", path.name)
        await bot.send_message(chat_id, text)


# ---- Нажатие на кнопку продукта ------------------------------------------
@router.message(StateFilter(None), F.text.in_(list(BUTTON_TO_PRODUCT)))
async def on_product(message: Message, bot: Bot, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user or not user["completed"]:
        await message.answer(NOT_REGISTERED)
        return
    lang = user["language"]
    product_id = BUTTON_TO_PRODUCT[message.text]

    member = await is_member(bot, message.from_user.id)
    if member is None:
        await message.answer(t(lang, "check_error"))
    elif member:
        await send_product(bot, message.chat.id, lang, product_id)
    else:
        await message.answer(
            t(lang, "need_join"), reply_markup=subscribe_kb(lang, product_id)
        )


# ---- «Я вступил / Проверить подписку» -------------------------------------
@router.callback_query(F.data.startswith("check:"))
async def on_check(call: CallbackQuery, bot: Bot, db: Database):
    product_id = call.data.split(":", 1)[1]
    if product_id not in PRODUCTS:
        await call.answer()
        return
    user = await db.get_user(call.from_user.id)
    lang = user["language"] if user else "ru"

    member = await is_member(bot, call.from_user.id)
    if member is None:
        await call.answer(t(lang, "check_error"), show_alert=True)
        return
    if not member:
        await call.answer(t(lang, "not_joined_alert"), show_alert=True)
        return

    await call.answer()
    try:  # убираем сообщение с просьбой вступить
        await bot.delete_message(call.from_user.id, call.message.message_id)
    except TelegramAPIError:
        pass
    await send_product(bot, call.from_user.id, lang, product_id)


# ---- Любой другой текст вне опросника -------------------------------------
@router.message(StateFilter(None), F.text)
async def fallback(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if user and user["completed"]:
        await message.answer(t(user["language"], "use_menu"), reply_markup=main_menu(user["language"]))
    else:
        await message.answer(NOT_REGISTERED)
