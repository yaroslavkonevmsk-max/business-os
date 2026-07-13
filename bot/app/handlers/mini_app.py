from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.keyboards.inline import mini_app_button
from app.config import settings

router = Router()


@router.message(Command("app"))
async def cmd_app(message: Message):
    """Open Mini App button."""
    # Use API_URL as base for Mini App URL
    mini_app_url = f"{settings.API_URL}/mini-app"
    await message.answer(
        "🚀 <b>Дашборд Business OS</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть Mini App в Telegram:",
        reply_markup=mini_app_button(mini_app_url)
    )
