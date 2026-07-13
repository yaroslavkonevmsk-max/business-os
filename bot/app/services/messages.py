from datetime import datetime
from typing import Any


def format_currency(amount: float | int) -> str:
    """Format amount as Russian currency string."""
    return f"{amount:,.0f} ₽".replace(",", " ")


def format_number(num: float | int) -> str:
    """Format number with spaces as thousand separators."""
    return f"{num:,.0f}".replace(",", " ")


def format_date(date_str: str | None) -> str:
    """Format ISO date string to DD.MM.YYYY."""
    if not date_str:
        return "—"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except (ValueError, AttributeError):
        return str(date_str)


def format_date_words(date_str: str) -> str:
    """Format date in Russian words (simplified)."""
    months = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return f'"{dt.day}" {months[dt.month]} {dt.year} г.'
    except (ValueError, AttributeError):
        return str(date_str)


def pulse_message(data: dict[str, Any]) -> str:
    """Format Pulse analytics data into a Telegram message."""
    month = data.get("month", datetime.now().strftime("%B"))
    year = data.get("year", datetime.now().year)
    revenue = data.get("revenue", 0)
    expenses = data.get("expenses", 0)
    profit = data.get("profit", 0)
    tax_regime = data.get("tax_regime", "УСН")
    tax_amount = data.get("tax_amount", 0)
    deadline = data.get("deadline", "—")
    days_left = data.get("days_left", 0)
    new_clients = data.get("new_clients", 0)
    repeat_clients = data.get("repeat_clients", 0)
    top_client_name = data.get("top_client_name", "—")
    top_client_revenue = data.get("top_client_revenue", 0)
    change_percent = data.get("change_percent", 0)
    prev_month = data.get("prev_month", "прошлому месяцу")
    ai_insight = data.get("ai_insight", "")

    lines = [
        f"📊 <b>Пульс бизнеса</b> — {month} {year}",
        "",
        f"💰 Выручка: <b>{format_currency(revenue)}</b> ({change_percent:+d}% к {prev_month})",
        f"📉 Расходы: <b>{format_currency(expenses)}</b>",
        f"✅ Прибыль: <b>{format_currency(profit)}</b>",
        f"🏦 Налог {tax_regime} к уплате: <b>{format_currency(tax_amount)}</b>",
        f"   (срок: {deadline}, осталось {days_left} дн.)",
        "",
        f"👥 Новых клиентов: {new_clients}",
        f"🔄 Повторных: {repeat_clients}",
        f"⭐ Топ-клиент: {top_client_name} ({format_currency(top_client_revenue)})",
    ]
    
    if ai_insight:
        lines.extend(["", f"💡 {ai_insight}"])
    
    return "\n".join(lines)


def new_payment_notification(data: dict[str, Any]) -> str:
    """Format notification for new payment."""
    amount = data.get("amount", 0)
    client_name = data.get("client_name", "—")
    description = data.get("description", "—")
    is_new_client = data.get("is_new_client", False)
    tax_regime = data.get("tax_regime", "УСН")
    tax_amount = data.get("tax_amount", 0)

    lines = [
        f"💰 <b>+{format_currency(amount)}</b> от {client_name}",
        f"   Назначение: {description}",
    ]
    
    if is_new_client:
        lines.append("   👤 Новый клиент создан автоматически")
    
    lines.extend([
        "",
        f"Налог {tax_regime} обновлён: к уплате {format_currency(tax_amount)}",
    ])
    
    return "\n".join(lines)


def morning_briefing(data: dict[str, Any]) -> str:
    """Format morning briefing message."""
    date_str = data.get("date", datetime.now().strftime("%d.%m.%Y"))
    yesterday_count = data.get("yesterday_count", 0)
    yesterday_amount = data.get("yesterday_amount", 0)
    new_client_name = data.get("new_client_name", "—")
    new_client_amount = data.get("new_client_amount", 0)
    tax_amount = data.get("tax_amount", 0)
    deadline = data.get("deadline", "—")
    today_expense_name = data.get("today_expense_name", "—")
    today_expense_amount = data.get("today_expense_amount", 0)
    ai_tip = data.get("ai_tip", "")

    lines = [
        f"Доброе утро! ☀️ Брифинг на {date_str}:",
        "",
        f"• 💰 Вчера: +{yesterday_count} поступлений на {format_currency(yesterday_amount)}",
        f"• 👤 Новый клиент: {new_client_name} ({format_currency(new_client_amount)})",
        f"• 📊 Налог к уплате: {format_currency(tax_amount)} (срок: {deadline})",
        f"• 💸 Расход сегодня: {today_expense_name} {format_currency(today_expense_amount)}",
    ]
    
    if ai_tip:
        lines.extend(["", f"💡 {ai_tip}"])
    
    return "\n".join(lines)
