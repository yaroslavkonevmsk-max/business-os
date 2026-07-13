from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.states.document_states import DocumentCreation
from app.keyboards.inline import (
    document_type_selector,
    client_selector,
    confirm_cancel,
    add_item_or_finish,
)
from app.services.api_client import ApiClient, ApiClientError
from app.services.validators import validate_amount, parse_date
from app.services.messages import format_currency

router = Router()


async def start_create_document(
    message: Message,
    state: FSMContext,
    api_token: str | None = None,
    doc_type: str | None = None,
    client_name: str | None = None,
    amount: float | None = None,
    description: str | None = None,
):
    """Entry point for document creation FSM."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    await state.set_state(DocumentCreation.select_type)
    await state.update_data(
        api_token=api_token,
        items=[],
    )
    
    if doc_type:
        await state.update_data(doc_type=doc_type)
        if client_name:
            await state.update_data(client_name=client_name)
        if amount:
            await state.update_data(total_amount=amount)
        if description:
            await state.update_data(description=description)
        
        # If we have enough pre-filled data, skip to confirmation or items
        if client_name and amount and description:
            # Skip to date
            await message.answer(
                f"📄 <b>Создание документа</b>\n"
                f"Тип: {doc_type}\n"
                f"Клиент: {client_name}\n"
                f"Сумма: {format_currency(amount)}\n"
                f"Услуги: {description}\n\n"
                f"Введите дату документа (ДД.ММ.ГГГГ) или '-' для сегодня:"
            )
            await state.set_state(DocumentCreation.enter_date)
            return
        
        # Need client selection
        await message.answer(
            f"Тип документа: <b>{doc_type}</b>. Теперь выберите клиента:",
            reply_markup=client_selector([])  # Simplified: manual input
        )
        await state.set_state(DocumentCreation.select_client)
    else:
        await message.answer(
            "📄 <b>Создание документа</b>\nВыберите тип:",
            reply_markup=document_type_selector()
        )


@router.callback_query(F.data.startswith("doc_type:"), StateFilter(DocumentCreation.select_type))
async def process_doc_type(callback: CallbackQuery, state: FSMContext):
    doc_type = callback.data.split(":")[1]
    await state.update_data(doc_type=doc_type)
    await callback.message.edit_text(
        f"Тип: <b>{doc_type}</b>. Введите имя клиента или выберите из списка:"
    )
    await state.set_state(DocumentCreation.select_client)
    await callback.answer()


@router.message(StateFilter(DocumentCreation.select_client))
async def process_client(message: Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    await message.answer(
        "Введите название услуги/товара для первой позиции:\n"
        "(или введите сумму сразу, если одна позиция)"
    )
    await state.set_state(DocumentCreation.enter_items)


@router.message(StateFilter(DocumentCreation.enter_items))
async def process_item(message: Message, state: FSMContext):
    """Parse item: name quantity price. For MVP, simplified to single line."""
    text = message.text.strip()
    
    # Try to parse as "name quantity price" or just "name"
    parts = text.rsplit(" ", 2)
    if len(parts) >= 3:
        try:
            price = float(parts[-1].replace(",", "."))
            qty = int(parts[-2])
            name = " ".join(parts[:-2])
        except ValueError:
            name = text
            qty = 1
            price = 0.0
    else:
        name = text
        qty = 1
        price = 0.0
    
    data = await state.get_data()
    items = data.get("items", [])
    items.append({
        "name": name,
        "quantity": qty,
        "unit": "шт",
        "price": price,
        "total": qty * price,
    })
    await state.update_data(items=items)
    
    total = sum(item["total"] for item in items)
    await message.answer(
        f"✅ Добавлено: {name} — {qty} × {price:,.2f} = {total:,.2f} ₽\n\n"
        f"Выберите действие:",
        reply_markup=add_item_or_finish()
    )
    await state.set_state(DocumentCreation.ask_add_item)


@router.callback_query(F.data == "item:add", StateFilter(DocumentCreation.ask_add_item))
async def add_another_item(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите следующую позицию (название количество цена):")
    await state.set_state(DocumentCreation.enter_items)
    await callback.answer()


@router.callback_query(F.data == "item:finish", StateFilter(DocumentCreation.ask_add_item))
async def finish_items(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get("items", [])
    total = sum(item["total"] for item in items)
    await state.update_data(total_amount=total)
    await callback.message.edit_text(
        f"Итого: <b>{format_currency(total)}</b>\n\n"
        f"Введите дату документа (ДД.ММ.ГГГГ) или '-' для сегодня:"
    )
    await state.set_state(DocumentCreation.enter_date)
    await callback.answer()


@router.message(StateFilter(DocumentCreation.enter_date))
async def process_date(message: Message, state: FSMContext):
    date_str = parse_date(message.text)
    if not date_str:
        await message.answer("❌ Неверный формат даты. Введите ДД.ММ.ГГГГ или '-':")
        return
    
    await state.update_data(date=date_str)
    data = await state.get_data()
    
    preview = (
        f"📄 <b>Предпросмотр документа</b>\n\n"
        f"Тип: <b>{data['doc_type']}</b>\n"
        f"Клиент: {data.get('client_name', '—')}\n"
        f"Дата: {date_str}\n"
        f"Сумма: {format_currency(data.get('total_amount', 0))}\n"
        f"Позиции:\n"
    )
    for idx, item in enumerate(data.get("items", []), 1):
        preview += f"{idx}. {item['name']} — {item['quantity']} × {item['price']:,.2f} = {item['total']:,.2f} ₽\n"
    
    await message.answer(preview, reply_markup=confirm_cancel())
    await state.set_state(DocumentCreation.confirm)


@router.callback_query(F.data == "confirm", StateFilter(DocumentCreation.confirm))
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("api_token")
    
    async with ApiClient(token) as client:
        try:
            result = await client.post("/api/v1/documents", json={
                "type": data["doc_type"],
                "client_name": data.get("client_name"),
                "total_amount": data.get("total_amount", 0),
                "date": data.get("date"),
                "items": data.get("items", []),
                "notes": data.get("description", ""),
            })
            doc_id = result.get("id", "?")
            await callback.message.edit_text(
                f"✅ Документ #{doc_id} успешно создан!\n"
                f"Он будет доступен в разделе «Документы».",
            )
        except ApiClientError as e:
            await callback.message.edit_text(f"❌ Ошибка создания документа: {e.detail}")
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка: {e}")
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel", StateFilter(DocumentCreation.confirm))
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Создание документа отменено.")
    await state.clear()
    await callback.answer()
