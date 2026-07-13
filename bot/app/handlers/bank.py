from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("bank"))
async def cmd_bank(message: Message, api_token: str | None = None):
    """Handle bank connection commands."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    text = (
        "🏦 <b>Банковский модуль</b>\n\n"
        "Доступные банки:\n"
        "• Т-Банк (Tinkoff)\n"
        "• СберБанк (в разработке)\n\n"
        "Для подключения используйте Mini App или настройки."
    )
    await message.answer(text)
