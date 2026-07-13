from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from app.keyboards.main_menu import get_main_menu, get_unauthorized_menu
from app.services.api_client import ApiClient, ApiClientError
from app.services.messages import pulse_message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, api_token: str | None = None):
    """Handle /start: greet user and show menu."""
    user = message.from_user
    if api_token:
        await message.answer(
            f"Привет, {user.first_name}! 👋\n"
            "Я — ваш бизнес-ассистент. Буду помогать с документами, расходами и налогами.",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            f"Привет, {user.first_name}! 👋\n"
            "Добро пожаловать в Business OS. Нажмите «Начать» для регистрации.",
            reply_markup=get_unauthorized_menu()
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help: list commands."""
    text = (
        "🤖 <b>Команды бота</b>\n\n"
        "/start — Начать работу\n"
        "/pulse — Пульс бизнеса\n"
        "/clients — Мои клиенты\n"
        "/documents — Документы\n"
        "/expenses — Расходы\n"
        "/taxes — Налоги\n"
        "/settings — Настройки\n"
        "/support — Поддержка\n\n"
        "💡 Также можно писать естественным языком: «Счёт Иванову на 30000»"
    )
    await message.answer(text)


@router.message(Command("pulse"))
async def cmd_pulse(message: Message, api_token: str | None = None):
    """Handle /pulse: fetch and display business pulse."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    async with ApiClient(api_token) as client:
        try:
            data = await client.get("/api/v1/analytics/pulse")
            await message.answer(pulse_message(data))
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка получения данных: {e.detail}")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("clients"))
async def cmd_clients(message: Message, api_token: str | None = None):
    """Handle /clients: list clients."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    async with ApiClient(api_token) as client:
        try:
            result = await client.get("/api/v1/clients", params={"page": 1, "limit": 10})
            clients = result.get("items", [])
            if not clients:
                await message.answer("👥 У вас пока нет клиентов. Добавьте первого через меню или команду.")
                return
            
            lines = ["👥 <b>Клиенты</b>\n"]
            for idx, c in enumerate(clients, 1):
                lines.append(f"{idx}. {c['name']}")
            await message.answer("\n".join(lines))
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка: {e.detail}")


@router.message(Command("documents"))
async def cmd_documents(message: Message, api_token: str | None = None):
    """Handle /documents: list recent documents."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    async with ApiClient(api_token) as client:
        try:
            result = await client.get("/api/v1/documents", params={"page": 1, "limit": 10})
            docs = result.get("items", [])
            if not docs:
                await message.answer("📄 У вас пока нет документов.")
                return
            
            lines = ["📄 <b>Документы</b>\n"]
            for d in docs:
                lines.append(f"• {d['type']} #{d['number']} — {d.get('total_amount', 0):,.0f} ₽")
            await message.answer("\n".join(lines))
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка: {e.detail}")


@router.message(Command("expenses"))
async def cmd_expenses(message: Message, api_token: str | None = None):
    """Handle /expenses: list recent expenses."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    async with ApiClient(api_token) as client:
        try:
            result = await client.get("/api/v1/expenses", params={"page": 1, "limit": 10})
            expenses = result.get("items", [])
            if not expenses:
                await message.answer("📉 У вас пока нет расходов.")
                return
            
            lines = ["📉 <b>Расходы</b>\n"]
            for e in expenses:
                lines.append(f"• {e['category']}: {e['amount']:,.0f} ₽")
            await message.answer("\n".join(lines))
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка: {e.detail}")


@router.message(Command("taxes"))
async def cmd_taxes(message: Message, api_token: str | None = None):
    """Handle /taxes: show current tax status."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    async with ApiClient(api_token) as client:
        try:
            result = await client.get("/api/v1/taxes")
            tax = result.get("current", {})
            text = (
                f"💰 <b>Налоги</b>\n\n"
                f"Режим: {tax.get('tax_regime', '—')}\n"
                f"Период: {tax.get('period', '—')}\n"
                f"К уплате: {tax.get('tax_amount', 0):,.0f} ₽\n"
                f"Срок: {tax.get('deadline', '—')}\n"
                f"Статус: {tax.get('status', '—')}"
            )
            await message.answer(text)
        except ApiClientError as e:
            await message.answer(f"❌ Ошибка: {e.detail}")


@router.message(Command("settings"))
async def cmd_settings(message: Message, api_token: str | None = None):
    """Handle /settings: show settings."""
    if not api_token:
        await message.answer("⚠️ Требуется авторизация. Нажмите /start")
        return
    
    from app.keyboards.inline import settings_menu
    await message.answer("⚙️ <b>Настройки</b>\nВыберите раздел:", reply_markup=settings_menu())


@router.message(Command("support"))
async def cmd_support(message: Message):
    """Handle /support: contact info."""
    await message.answer(
        "🆘 <b>Поддержка</b>\n\n"
        "Если у вас возникли вопросы, напишите нам: @business_os_support\n"
        "Или отправьте email на support@business-os.ru"
    )


@router.message(F.text == "🚀 Начать")
async def text_start(message: Message, api_token: str | None = None):
    await cmd_start(message, api_token)


@router.message(F.text == "❓ Помощь")
async def text_help(message: Message):
    await cmd_help(message)


@router.message(F.text == "📊 Пульс")
async def text_pulse(message: Message, api_token: str | None = None):
    await cmd_pulse(message, api_token)


@router.message(F.text == "👥 Клиенты")
async def text_clients(message: Message, api_token: str | None = None):
    await cmd_clients(message, api_token)


@router.message(F.text == "📄 Документы")
async def text_documents(message: Message, api_token: str | None = None):
    await cmd_documents(message, api_token)


@router.message(F.text == "📉 Расходы")
async def text_expenses(message: Message, api_token: str | None = None):
    await cmd_expenses(message, api_token)


@router.message(F.text == "💰 Налоги")
async def text_taxes(message: Message, api_token: str | None = None):
    await cmd_taxes(message, api_token)


@router.message(F.text == "⚙️ Настройки")
async def text_settings(message: Message, api_token: str | None = None):
    await cmd_settings(message, api_token)
