from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
MATERIALS_DIR = BASE_DIR / "materials"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    BOT_TOKEN: str
    ADMIN_ID: int
    TARGET_GROUP_ID: int
    TARGET_GROUP_LINK: str
    DB_PATH: str = str(BASE_DIR / "bot.db")


settings = Settings()

AGE_RANGES = ["14-18", "18-25", "25-35", "35-50", "50+"]

# ---------------------------------------------------------------------------
# ПРОДУКТЫ / ЛИД-МАГНИТЫ
# Чтобы добавить новый продукт, достаточно добавить новый ключ в этот словарь:
#   "button" — текст кнопки меню по языкам
#   "text"   — сообщение при выдаче (HTML) по языкам
#   "link"   — ссылка (или None)
#   "file"   — PDF из папки materials/: строка (один файл для всех языков),
#              словарь {"uz": "...", "ru": "..."} или None
# Меню, проверка подписки и выдача подхватят его автоматически.
# ---------------------------------------------------------------------------
PRODUCTS: dict[str, dict] = {
    "calc": {
        "button": {
            "uz": "Unit Economics Calculator",
            "ru": "Unit Economics Calculator",
        },
        "text": {
            "uz": "📊 <b>Unit Economics Calculator</b>\n\nHar bir mahsulotning haqiqiy foydasini hisoblang.",
            "ru": "📊 <b>Unit Economics Calculator</b>\n\nПосчитайте реальную прибыль по каждому товару.",
        },
        "link": "https://uzumbyamirjon.netlify.app/",
        "file": None,
    },
    "register": {
        "button": {
            "uz": "Uzum Market'da ro'yxatdan o'tish",
            "ru": "Как зарегистрироваться в Uzum Market",
        },
        "text": {
            "uz": "📝 <b>Uzum Market'da ro'yxatdan o'tish</b>\n\nQadamma-qadam yo'riqnoma tayyor.",
            "ru": "📝 <b>Как зарегистрироваться в Uzum Market</b>\n\nПошаговая инструкция готова.",
        },
        "link": None,
        "file": {"uz": "register_uz.pdf", "ru": "register_ru.pdf"},
    },
    "start_selling": {
        "button": {
            "uz": "Uzum Market'da sotishni boshlash",
            "ru": "Как начать продавать в Uzum Market",
        },
        "text": {
            "uz": "🚀 <b>Uzum Market'da sotishni boshlash</b>\n\nBirinchi sotuvlar uchun qo'llanma.",
            "ru": "🚀 <b>Как начать продавать в Uzum Market</b>\n\nГайд для первых продаж.",
        },
        "link": "https://uzumbyamirjon.netlify.app/",  # TODO: ваша ссылка
        "file": {"uz": "start_selling_uz.pdf", "ru": "start_selling_ru.pdf"},
    },
}

# Текст кнопки (на любом языке) -> id продукта
BUTTON_TO_PRODUCT: dict[str, str] = {
    text: pid for pid, p in PRODUCTS.items() for text in p["button"].values()
}


def get_product_file(product_id: str, lang: str) -> Path | None:
    f = PRODUCTS[product_id].get("file")
    if isinstance(f, dict):
        f = f.get(lang)
    return MATERIALS_DIR / f if f else None
