from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery):
    """Do nothing for placeholder buttons (e.g. page counters)."""
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def on_cancel(callback: CallbackQuery):
    """Generic cancel callback."""
    await callback.message.edit_text("❌ Действие отменено.")
    await callback.answer()


@router.callback_query(F.data == "doc:list")
async def on_doc_list(callback: CallbackQuery, api_token: str | None = None):
    """Return to document list from detail view."""
    if not api_token:
        await callback.answer("⚠️ Требуется авторизация", show_alert=True)
        return
    
    from app.handlers.commands import cmd_documents
    await callback.message.delete()
    await cmd_documents(callback.message, api_token)
    await callback.answer()


@router.callback_query(F.data.startswith("page:"))
async def on_page(callback: CallbackQuery, api_token: str | None = None):
    """Handle pagination callbacks."""
    page = int(callback.data.split(":")[1])
    await callback.answer(f"Страница {page}")
    # Actual page switching would be implemented per-list handler
