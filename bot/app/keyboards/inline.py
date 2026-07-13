from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ─── Document Actions ───

def document_actions(document_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📎 Скачать PDF",
        callback_data=f"doc:download:{document_id}"
    )
    builder.button(
        text="📧 Отправить email",
        callback_data=f"doc:email:{document_id}"
    )
    builder.button(
        text="💬 Отправить в Telegram",
        callback_data=f"doc:send:{document_id}"
    )
    builder.button(
        text="✏️ Редактировать",
        callback_data=f"doc:edit:{document_id}"
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=f"doc:delete:{document_id}"
    )
    builder.button(
        text="◀️ Назад к списку",
        callback_data="doc:list"
    )
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def confirm_cancel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm")
    builder.button(text="❌ Отменить", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


# ─── Document Type Selection ───

def document_type_selector() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧾 Счёт", callback_data="doc_type:invoice")
    builder.button(text="📋 Акт", callback_data="doc_type:act")
    builder.button(text="📦 Накладная", callback_data="doc_type:waybill")
    builder.button(text="📝 Договор ГПХ", callback_data="doc_type:gph_contract")
    builder.button(text="📊 Отчёт", callback_data="doc_type:report")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


# ─── Client Selection ───

def client_selector(clients: list[dict], page: int = 1, has_next: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, client in enumerate(clients, start=1):
        builder.button(
            text=f"{idx}. {client['name']}",
            callback_data=f"client:select:{client['id']}"
        )
    builder.button(text="➕ Новый клиент", callback_data="client:new")
    builder.button(text="🔍 Поиск", callback_data="client:search")
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(("◀️ Назад", f"client:page:{page - 1}"))
    if has_next:
        nav_buttons.append(("Вперёд ▶️", f"client:page:{page + 1}"))
    for text, data in nav_buttons:
        builder.button(text=text, callback_data=data)
    
    builder.adjust(1, 1, 1, len(nav_buttons))
    return builder.as_markup()


# ─── Expense Categories ───

def expense_categories() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    categories = [
        ("🏢 Аренда", "rent"),
        ("💻 Софт", "software"),
        ("🖥 Оборудование", "hardware"),
        ("🚗 Транспорт", "transport"),
        ("📣 Маркетинг", "marketing"),
        ("🖇 Офис", "office"),
        ("💸 Налоги", "taxes"),
        ("👥 Зарплата", "salary"),
        ("📦 Другое", "other"),
    ]
    for text, cat_id in categories:
        builder.button(text=text, callback_data=f"expense:cat:{cat_id}")
    builder.adjust(3, 3, 3)
    return builder.as_markup()


# ─── Client Types ───

def client_types() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Физлицо", callback_data="client_type:individual")
    builder.button(text="🏢 Компания", callback_data="client_type:company")
    builder.button(text="📋 ИП", callback_data="client_type:ip")
    builder.adjust(3)
    return builder.as_markup()


# ─── Settings Menu ───

def settings_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Имя", callback_data="settings:name")
    builder.button(text="📊 Налоговый режим", callback_data="settings:tax_regime")
    builder.button(text="🔔 Уведомления", callback_data="settings:notifications")
    builder.button(text="🏦 Банк", callback_data="settings:bank")
    builder.adjust(2, 2)
    return builder.as_markup()


# ─── Add Item or Finish ───

def add_item_or_finish() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить позицию", callback_data="item:add")
    builder.button(text="✅ Завершить", callback_data="item:finish")
    builder.adjust(2)
    return builder.as_markup()


# ─── Mini App Button ───

def mini_app_button(url: str) -> InlineKeyboardMarkup:
    from aiogram.types import WebAppInfo
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Открыть дашборд",
        web_app=WebAppInfo(url=url)
    )
    return builder.as_markup()
