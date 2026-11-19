import re

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import Database
from keyboards import language_kb, main_menu
from states import Survey
from texts import CHOOSE_LANGUAGE, t

router = Router()

SOURCE_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")


@router.message(CommandStart())
async def cmd_start(
    message: Message, command: CommandObject, state: FSMContext, db: Database
):
    await state.clear()
    user = await db.get_user(message.from_user.id)

    # Уже прошёл опросник -> сразу главное меню
    if user and user["completed"]:
        await message.answer(
            t(user["language"], "menu_welcome"), reply_markup=main_menu(user["language"])
        )
        return

    # Новый пользователь -> опросник. Метка трафика: /start instagram
    source = None
    if command.args and SOURCE_RE.fullmatch(command.args.strip()):
        source = command.args.strip().lower()

    await state.update_data(source=source)
    await state.set_state(Survey.language)
    await message.answer(CHOOSE_LANGUAGE, reply_markup=language_kb())
