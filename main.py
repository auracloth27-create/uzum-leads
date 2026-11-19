import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import Database
from handlers import admin, menu, start, survey


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    db = Database(settings.DB_PATH)
    await db.connect()

    bot = Bot(
        settings.9240865638:AAHFfm9cVM4C0rUhsjqF_UQdr2F4hv7ZNNo,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["db"] = db  # доступна во всех хэндлерах как аргумент `db`

    # Порядок важен: admin -> start -> survey -> menu (menu содержит fallback)
    dp.include_routers(admin.router, start.router, survey.router, menu.router)

    try:
        await bot.delete_webhook()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
