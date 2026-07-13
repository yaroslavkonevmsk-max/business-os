from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command

from app.states.settings_states import SettingsUpdate
from app.keyboards.inline import settings_menu
from app.services.api_client import ApiClient, ApiClientError

router = Router()


@router.callback_query(F.data.startswith("settings:"))
async def on_settings_callback(callback: CallbackQuery, state: FSMContext, api_token: str | None = None):
    """Handle settings inline buttons."""
    if not api_token:
        await callback.answer("⚠️ Требуется авторизация", show_alert=True)
        return
    
    field = callback.data.split(":")[1]
    await state.set_state(SettingsUpdate.enter_value)
    await state.update_data(api_token=api_token, field=field)
    
    prompts = {
        "name": "Введите новое имя/название компании:",
        "tax_regime": "Выберите режим: usn_income, usn_income_expense, npd, patent",
        "notifications": "Включить уведомления? (да/нет)",
        "bank": "Используйте /bank для подключения банка.",
    }
    
    await callback.message.edit_text(prompts.get(field, "Введите новое значение:"))
    await callback.answer()


@router.message(StateFilter(SettingsUpdate.enter_value))
async def process_settings_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    token = data.get("api_token")
    value = message.text.strip()
    
    if field == "notifications":
        value = value.lower() in ("да", "yes", "1", "true", "вкл")
    
    async with ApiClient(token) as client:
        try:
            await client.put("/api/v1/users/me/settings", json={field: value})
            await message.answer(f"✅ Настройка «{field}» обновлена.")
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка: {e.detail}")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()


@router.message(Command("settings"))
async def cmd_settings_text(message: Message, api_token: str | None = None):
    """Show settings menu (also handled in commands.py)."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    await message.answer("⚙️ <b>Настройки</b>\nВыберите раздел:", reply_markup=settings_menu())
