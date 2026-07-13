from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def paginator(
    current_page: int,
    total_pages: int,
    prefix: str = "page",
) -> InlineKeyboardMarkup:
    """Build pagination inline keyboard."""
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.button(
            text="◀️ Предыдущие",
            callback_data=f"{prefix}:{current_page - 1}"
        )
    
    builder.button(
        text=f"Страница {current_page}/{total_pages}",
        callback_data="noop"
    )
    
    if current_page < total_pages:
        builder.button(
            text="Следующие ▶️",
            callback_data=f"{prefix}:{current_page + 1}"
        )
    
    builder.adjust(3)
    return builder.as_markup()
