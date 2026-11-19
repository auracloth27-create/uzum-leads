import csv
import html
import io

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from config import settings
from database import Database

router = Router()
router.message.filter(F.from_user.id == settings.ADMIN_ID)


@router.message(Command("stats"))
async def stats(message: Message, db: Database):
    s = await db.stats()
    lines = [
        "📊 <b>Статистика</b>",
        f"Запустили бота: {s['total']}",
        f"Прошли опросник: {s['done']}",
        f"Из них продавцы Uzum: {s['sellers']}",
        "",
        "<b>По источникам</b> (запустили / прошли):",
    ]
    for r in s["by_source"]:
        lines.append(f"• {html.escape(r['src'])}: {r['started']} / {r['done'] or 0}")
    await message.answer("\n".join(lines))


@router.message(Command("export"))
async def export(message: Message, db: Database):
    rows = await db.all_completed()
    buf = io.StringIO()
    fields = [
        "user_id", "username", "language", "name", "is_uzum_seller",
        "age_range", "phone", "source", "created_at", "completed_at",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = buf.getvalue().encode("utf-8-sig")  # BOM — чтобы Excel открыл кириллицу
    await message.answer_document(BufferedInputFile(data, filename="leads.csv"))
