from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import logging
import redis.asyncio as redis

from app.config import settings
from app.services.api_client import ApiClient, ApiAuthError

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    Authenticate user via backend API.
    - Extracts Telegram user info
    - Checks Redis for cached JWT
    - If missing, calls POST /api/v1/auth/telegram to register/obtain JWT
    - Injects `api_token` and `redis` into handler data
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            data["api_token"] = None
            data["redis"] = self.redis
            return await handler(event, data)
        
        token_key = f"jwt:{user.id}"
        token = await self.redis.get(token_key)
        
        if not token:
            # Register or login via backend
            async with ApiClient() as client:
                try:
                    result = await client.post(
                        "/api/v1/auth/telegram",
                        json={
                            "telegram_id": user.id,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "username": user.username,
                            "language_code": user.language_code,
                            "is_premium": getattr(user, "is_premium", None),
                        }
                    )
                    token = result.get("access_token")
                    if token:
                        await self.redis.setex(
                            token_key,
                            settings.JWT_TTL_SECONDS,
                            token
                        )
                        logger.info(f"JWT obtained for user {user.id}")
                except ApiAuthError:
                    logger.warning(f"Auth error for user {user.id}")
                    token = None
                except Exception as e:
                    logger.error(f"Backend auth error: {e}")
                    token = None
        
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        
        data["api_token"] = token
        data["redis"] = self.redis
        return await handler(event, data)
