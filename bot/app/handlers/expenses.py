from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from datetime import datetime

from app.states.expense_states import ExpenseAddition
from app.keyboards.inline import confirm_cancel, expense_categories
from app.services.api_client import ApiClient, ApiClientError
from app.services.validators import validate_amount
from app.services.messages import format_currency

router = Router()


async def start_add_expense(
    message: Message,
    state: FSMContext,
    api_token: str | None = None,
    amount: float | None = None,
    description: str | None = None,
):
    """Entry point for expense addition FSM."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    await state.set_state(ExpenseAddition.enter_amount)
    await state.update_data(api_token=api_token)
    
    if amount and amount > 0:
        await state.update_data(amount=amount)
        if description:
            await state.update_data(description=description)
            # Try to auto-categorize via description (MVP: ask user)
            await message.answer(
                f"💸 Сумма: <b>{format_currency(amount)}</b>\n"
                f"Описание: {description}\n\n"
                f"Выберите категорию:",
                reply_markup=expense_categories()
            )
            await state.set_state(ExpenseAddition.select_category)
        else:
            await message.answer(
                f"💸 Сумма: <b>{format_currency(amount)}</b>\n"
                f"Введите описание (или '-' для пропуска):"
            )
            await state.set_state(ExpenseAddition.enter_description)
    else:
        await message.answer("💸 <b>Новый расход</b>\nВведите сумму:")


@router.message(StateFilter(ExpenseAddition.enter_amount))
async def process_amount(message: Message, state: FSMContext):
    amount = validate_amount(message.text)
    if amount is None:
        await message.answer("❌ Неверная сумма. Введите число больше 0:")
        return
    
    await state.update_data(amount=amount)
    await message.answer(
        f"Сумма: <b>{format_currency(amount)}</b>\n\n"
        f"Выберите категорию:",
        reply_markup=expense_categories()
    )
    await state.set_state(ExpenseAddition.select_category)


@router.callback_query(F.data.startswith("expense:cat:"), StateFilter(ExpenseAddition.select_category))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[2]
    await state.update_data(category=category)
    await callback.message.edit_text("Введите описание (или '-' для пропуска):")
    await state.set_state(ExpenseAddition.enter_description)
    await callback.answer()


@router.message(StateFilter(ExpenseAddition.enter_description))
async def process_description(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else ""
    await state.update_data(description=desc)
    data = await state.get_data()
    
    preview = (
        f"💸 <b>Новый расход</b>\n\n"
        f"Категория: <b>{data['category']}</b>\n"
        f"Сумма: {format_currency(data['amount'])}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y')}\n"
        f"Описание: {desc or '—'}"
    )
    await message.answer(preview, reply_markup=confirm_cancel())
    await state.set_state(ExpenseAddition.confirm)


@router.callback_query(F.data == "confirm", StateFilter(ExpenseAddition.confirm))
async def confirm_expense(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("api_token")
    
    async with ApiClient(token) as client:
        try:
            await client.post("/api/v1/expenses", json={
                "amount": data["amount"],
                "category": data["category"],
                "description": data.get("description"),
                "date": datetime.now().isoformat(),
            })
            await callback.message.edit_text("✅ Расход добавлен! Налог обновлён.")
        except ApiClientError as e:
            await callback.message.edit_text(f"❌ Ошибка: {e.detail}")
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {e}")
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel", StateFilter(ExpenseAddition.confirm))
async def cancel_expense(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление расхода отменено.")
    await state.clear()
    await callback.answer()
