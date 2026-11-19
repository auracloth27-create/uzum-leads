from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import AGE_RANGES, PRODUCTS, settings
from texts import LANGUAGES, t


def language_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code, label in LANGUAGES.items():
        b.button(text=label, callback_data=f"lang:{code}")
    b.adjust(2)
    return b.as_markup()


def yes_no_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "yes"), callback_data="seller:yes")
    b.button(text=t(lang, "no"), callback_data="seller:no")
    b.adjust(2)
    return b.as_markup()


def age_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for age in AGE_RANGES:
        b.button(text=age, callback_data=f"age:{age}")
    b.adjust(2)
    return b.as_markup()


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=p["button"][lang])] for p in PRODUCTS.values()],
        resize_keyboard=True,
    )


def subscribe_kb(lang: str, product_id: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t(lang, "join_btn"), url=settings.TARGET_GROUP_LINK))
    b.row(
        InlineKeyboardButton(
            text=t(lang, "check_btn"), callback_data=f"check:{product_id}"
        )
    )
    return b.as_markup()
