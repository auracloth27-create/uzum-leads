DEFAULT_LANG = "ru"

LANGUAGES = {
    "uz": "🇺🇿 O'zbek tili",
    "ru": "🇷🇺 Русский язык",
}

CHOOSE_LANGUAGE = "Tilni tanlang / Выберите язык:"
NOT_REGISTERED = "Avval /start buyrug'ini yuboring.\nСначала отправьте команду /start."

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "ask_name": "Ismingizni yozing:",
        "invalid_name": "Iltimos, ismingizni matn ko'rinishida yozing (2–64 belgi).",
        "ask_seller": "Siz hozir Uzum Market'da sotuvchimisiz?",
        "yes": "Ha",
        "no": "Yo'q",
        "ask_age": "Yoshingizni tanlang:",
        "ask_phone": (
            "Telefon raqamingizni yuboring: pastdagi tugmani bosing "
            "yoki raqamni qo'lda yozing (masalan: +998901234567)."
        ),
        "share_phone": "📱 Telefon raqamni yuborish",
        "invalid_phone": "Raqam noto'g'ri formatda. Masalan: +998901234567",
        "invalid_contact": "Iltimos, o'zingizning telefon raqamingizni yuboring.",
        "use_buttons": "Iltimos, xabar ostidagi tugmalardan birini tanlang 👇",
        "survey_done": "✅ Rahmat! Anketa qabul qilindi.\n\nQuyidagi menyudan kerakli materialni tanlang 👇",
        "menu_welcome": "Asosiy menyu. Kerakli materialni tanlang 👇",
        "use_menu": "Iltimos, menyudagi tugmalardan foydalaning 👇",
        "need_join": (
            "Materialni olish uchun avval guruhimizga a'zo bo'ling, "
            "so'ng «Obunani tekshirish» tugmasini bosing 👇"
        ),
        "join_btn": "➡️ Guruhga qo'shilish",
        "check_btn": "✅ Qo'shildim / Obunani tekshirish",
        "not_joined_alert": "Obuna hali topilmadi. Avval guruhga a'zo bo'ling, so'ng qayta tekshiring.",
        "check_error": "Obunani tekshirib bo'lmadi. Birozdan so'ng qayta urinib ko'ring.",
    },
    "ru": {
        "ask_name": "Введите ваше имя:",
        "invalid_name": "Пожалуйста, введите имя текстом (2–64 символа).",
        "ask_seller": "Вы сейчас продаёте на Uzum Market?",
        "yes": "Да",
        "no": "Нет",
        "ask_age": "Выберите ваш возраст:",
        "ask_phone": (
            "Отправьте номер телефона: нажмите кнопку ниже "
            "или введите номер вручную (например: +998901234567)."
        ),
        "share_phone": "📱 Поделиться номером телефона",
        "invalid_phone": "Неверный формат номера. Пример: +998901234567",
        "invalid_contact": "Пожалуйста, отправьте свой собственный номер телефона.",
        "use_buttons": "Пожалуйста, выберите один из вариантов кнопками под сообщением 👇",
        "survey_done": "✅ Спасибо! Анкета принята.\n\nВыберите нужный материал в меню ниже 👇",
        "menu_welcome": "Главное меню. Выберите нужный материал 👇",
        "use_menu": "Пожалуйста, пользуйтесь кнопками меню 👇",
        "need_join": (
            "Чтобы получить материал, сначала вступите в нашу группу, "
            "затем нажмите «Проверить подписку» 👇"
        ),
        "join_btn": "➡️ Вступить в группу",
        "check_btn": "✅ Я вступил / Проверить подписку",
        "not_joined_alert": "Подписка пока не найдена. Сначала вступите в группу, затем проверьте снова.",
        "check_error": "Не удалось проверить подписку. Попробуйте чуть позже.",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else DEFAULT_LANG
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text
