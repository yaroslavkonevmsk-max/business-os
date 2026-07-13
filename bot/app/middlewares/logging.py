from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log all incoming messages and callbacks."""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        user_id = user.id if user else "unknown"
        username = user.username if user else "unknown"
        
        if isinstance(event, Message):
            text = event.text or event.caption or f"[{event.content_type}]"
            logger.info(f"MSG user={user_id}(@{username}): {text[:200]}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"CBQ user={user_id}(@{username}): {event.data}")
        
        return await handler(event, data)
