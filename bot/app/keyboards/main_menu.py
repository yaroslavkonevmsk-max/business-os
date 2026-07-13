from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Persistent main menu (ReplyKeyboardMarkup)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Пульс"),
                KeyboardButton(text="👥 Клиенты"),
                KeyboardButton(text="📄 Документы"),
            ],
            [
                KeyboardButton(text="💰 Налоги"),
                KeyboardButton(text="📉 Расходы"),
                KeyboardButton(text="⚙️ Настройки"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_unauthorized_menu() -> ReplyKeyboardMarkup:
    """Menu for unauthorized users."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать")],
            [KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )
