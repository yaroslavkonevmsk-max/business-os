import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.handlers.clients import start_add_client
from app.handlers.documents import start_create_document
from app.handlers.expenses import start_add_expense
from app.handlers.commands import cmd_pulse, cmd_clients, cmd_documents, cmd_expenses, cmd_taxes, cmd_settings
from app.services.validators import validate_amount

router = Router()

# ─── NLP-lite Regex Patterns ───

PATTERNS = {
    "pulse": re.compile(r'^(пульс|сводка|статус|как\s+дела)$', re.IGNORECASE),
    "clients": re.compile(r'^(клиенты|мои\s+клиенты)$', re.IGNORECASE),
    "client_detail": re.compile(r'^(?:клиент\s+(?:№?|#)?(\d+)|(\d+))$', re.IGNORECASE),
    "create_act": re.compile(r'^(акт|создать\s+акт|акт\s+выполненных\s+работ)$', re.IGNORECASE),
    "create_invoice": re.compile(
        r'^(?:сч[её]т|выставить\s+сч[её]т|сч[её]т\s+на\s+оплату)(?:\s+(.+))?$',
        re.IGNORECASE
    ),
    "invoice_nlp": re.compile(
        r'^(?:сч[её]т|акт)\s+(?:для\s+)?(.+?)\s+(?:на\s+)?(\d[\d\s,.]*)(?:\s*руб)?\s*(?:за\s+)?(.+)?$',
        re.IGNORECASE
    ),
    "expense": re.compile(
        r'^(?:расход|потратил|затрата)\s+(\d[\d\s,.]*)\s*(?:руб)?\s*(?:на\s+)?(.+)?$',
        re.IGNORECASE
    ),
    "expenses_list": re.compile(r'^(расходы|мои\s+расходы)$', re.IGNORECASE),
    "tax": re.compile(r'^(?:налог|сколько\s+налог|усн|ндфл)$', re.IGNORECASE),
    "debts": re.compile(r'^(?:долги|кто\s+должен|взаиморасчеты)$', re.IGNORECASE),
    "documents": re.compile(r'^(документы|мои\s+документы)$', re.IGNORECASE),
    "bank_connect": re.compile(r'^(?:банк|подключить\s+банк|т-банк|сбер)$', re.IGNORECASE),
    "settings": re.compile(r'^(?:настройки|профиль|мой\s+профиль)$', re.IGNORECASE),
}


@router.message(F.text)
async def handle_text(
    message: Message,
    state: FSMContext,
    api_token: str | None = None,
):
    """Main text message handler with NLP-lite."""
    
    # If user is in FSM, ignore NLP and let specific handlers work
    current_state = await state.get_state()
    if current_state:
        return
    
    text = message.text.strip()
    
    # 1. Pulse / Status
    if PATTERNS["pulse"].match(text):
        return await cmd_pulse(message, api_token)
    
    # 2. Clients list
    if PATTERNS["clients"].match(text):
        return await cmd_clients(message, api_token)
    
    # 3. Client detail
    if match := PATTERNS["client_detail"].match(text):
        client_id = match.group(1) or match.group(2)
        return await cmd_clients(message, api_token)  # Simplified: show list
    
    # 4. Complex NLP: "Счёт Иванову на 30000 за дизайн"
    if match := PATTERNS["invoice_nlp"].match(text):
        client_name = match.group(1).strip()
        amount_str = match.group(2).replace(" ", "").replace(",", ".")
        description = (match.group(3) or "").strip()
        amount = validate_amount(amount_str)
        doc_type = "invoice" if "сч" in text.lower() else "act"
        return await start_create_document(
            message, state, api_token,
            doc_type=doc_type,
            client_name=client_name,
            amount=amount,
            description=description,
        )
    
    # 5. Simple create act
    if PATTERNS["create_act"].match(text):
        return await start_create_document(message, state, api_token, doc_type="act")
    
    # 6. Simple create invoice
    if PATTERNS["create_invoice"].match(text):
        return await start_create_document(message, state, api_token, doc_type="invoice")
    
    # 7. Expense with amount and category
    if match := PATTERNS["expense"].match(text):
        amount_str = match.group(1).replace(" ", "").replace(",", ".")
        description = (match.group(2) or "").strip()
        amount = validate_amount(amount_str)
        return await start_add_expense(
            message, state, api_token,
            amount=amount,
            description=description,
        )
    
    # 8. Expenses list
    if PATTERNS["expenses_list"].match(text):
        return await cmd_expenses(message, api_token)
    
    # 9. Tax
    if PATTERNS["tax"].match(text):
        return await cmd_taxes(message, api_token)
    
    # 10. Debts
    if PATTERNS["debts"].match(text):
        return await message.answer(
            "💳 Взаиморасчёты будут доступны в следующем обновлении.\n"
            "Используйте /clients для просмотра клиентов."
        )
    
    # 11. Documents
    if PATTERNS["documents"].match(text):
        return await cmd_documents(message, api_token)
    
    # 12. Bank connect
    if PATTERNS["bank_connect"].match(text):
        from app.handlers.bank import cmd_bank
        return await cmd_bank(message, api_token)
    
    # 13. Settings
    if PATTERNS["settings"].match(text):
        return await cmd_settings(message, api_token)
    
    # Fallback
    await message.answer(
        "🤔 Не понял команду. Вот что я умею:\n\n"
        "• 📊 Пульс — бизнес-аналитика\n"
        "• 👥 Клиенты — список клиентов\n"
        "• 📄 Документы — акты и счета\n"
        "• 📉 Расходы — учёт расходов\n"
        "• 💰 Налоги — текущий налог\n"
        "• ⚙️ Настройки — профиль и банки\n\n"
        "Или просто напишите: «Счёт Иванову на 30000 за дизайн»"
    )
