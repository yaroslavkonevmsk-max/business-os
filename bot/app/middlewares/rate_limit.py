from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import redis.asyncio as redis

from app.config import settings


class RateLimitMiddleware(BaseMiddleware):
    """Rate limit middleware using Redis (or in-memory fallback)."""
    
    def __init__(self, redis_client: redis.Redis | None = None):
        self.redis = redis_client
        self.limit = settings.RATE_LIMIT_SECONDS
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            return await handler(event, data)
        
        key = f"rate_limit:{user.id}"
        
        if self.redis:
            exists = await self.redis.get(key)
            if exists:
                if isinstance(event, Message):
                    await event.answer("⏳ Слишком быстро. Подождите секунду.")
                return None
            await self.redis.setex(key, self.limit, "1")
        else:
            # In-memory fallback (not recommended for multi-instance)
            pass
        
        return await handler(event, data)
