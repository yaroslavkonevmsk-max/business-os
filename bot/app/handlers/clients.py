from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.states.client_states import ClientAddition
from app.keyboards.inline import confirm_cancel, client_types
from app.services.api_client import ApiClient, ApiClientError
from app.services.validators import validate_phone, validate_email, validate_inn

router = Router()


async def start_add_client(
    message: Message,
    state: FSMContext,
    api_token: str | None = None,
    name: str | None = None,
):
    """Entry point for client addition FSM."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    await state.set_state(ClientAddition.enter_name)
    await state.update_data(api_token=api_token)
    
    if name:
        await state.update_data(name=name)
        await message.answer(
            f"👤 Имя: <b>{name}</b>\n\n"
            f"Выберите тип клиента:",
            reply_markup=client_types()
        )
        await state.set_state(ClientAddition.enter_type)
    else:
        await message.answer("👤 <b>Новый клиент</b>\nВведите имя или название:")


@router.message(StateFilter(ClientAddition.enter_name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Выберите тип клиента:", reply_markup=client_types())
    await state.set_state(ClientAddition.enter_type)


@router.callback_query(F.data.startswith("client_type:"), StateFilter(ClientAddition.enter_type))
async def process_type(callback: CallbackQuery, state: FSMContext):
    client_type = callback.data.split(":")[1]
    await state.update_data(client_type=client_type)
    await callback.message.edit_text("Введите ИНН (опционально, '-' для пропуска):")
    await state.set_state(ClientAddition.enter_inn)
    await callback.answer()


@router.message(StateFilter(ClientAddition.enter_inn))
async def process_inn(message: Message, state: FSMContext):
    inn = message.text if message.text != "-" else None
    if inn and not validate_inn(inn):
        await message.answer("❌ ИНН должен содержать 10 или 12 цифр. Попробуйте ещё раз или '-' для пропуска:")
        return
    
    await state.update_data(inn=inn)
    await message.answer("Введите телефон (опционально, '-' для пропуска):")
    await state.set_state(ClientAddition.enter_phone)


@router.message(StateFilter(ClientAddition.enter_phone))
async def process_phone(message: Message, state: FSMContext):
    phone = message.text if message.text != "-" else None
    if phone and not validate_phone(phone):
        await message.answer("❌ Неверный формат телефона. Попробуйте ещё раз или '-' для пропуска:")
        return
    
    await state.update_data(phone=phone)
    await message.answer("Введите email (опционально, '-' для пропуска):")
    await state.set_state(ClientAddition.enter_email)


@router.message(StateFilter(ClientAddition.enter_email))
async def process_email(message: Message, state: FSMContext):
    email = message.text if message.text != "-" else None
    if email and not validate_email(email):
        await message.answer("❌ Неверный формат email. Попробуйте ещё раз или '-' для пропуска:")
        return
    
    await state.update_data(email=email)
    data = await state.get_data()
    
    preview = (
        f"👤 <b>Новый клиент</b>\n\n"
        f"Имя: <b>{data['name']}</b>\n"
        f"Тип: {data.get('client_type', '—')}\n"
        f"ИНН: {data.get('inn') or '—'}\n"
        f"Телефон: {data.get('phone') or '—'}\n"
        f"Email: {data.get('email') or '—'}"
    )
    await message.answer(preview, reply_markup=confirm_cancel())
    await state.set_state(ClientAddition.confirm)


@router.callback_query(F.data == "confirm", StateFilter(ClientAddition.confirm))
async def confirm_client(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("api_token")
    
    async with ApiClient(token) as client:
        try:
            await client.post("/api/v1/clients", json={
                "name": data["name"],
                "type": data.get("client_type"),
                "inn": data.get("inn"),
                "phone": data.get("phone"),
                "email": data.get("email"),
            })
            await callback.message.edit_text("✅ Клиент добавлен!")
        except ApiClientError as e:
            await callback.message.edit_text(f"❌ Ошибка: {e.detail}")
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {e}")
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel", StateFilter(ClientAddition.confirm))
async def cancel_client(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление клиента отменено.")
    await state.clear()
    await callback.answer()
