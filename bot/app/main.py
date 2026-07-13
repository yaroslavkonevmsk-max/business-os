import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from app.config import settings
from app.middlewares.auth import AuthMiddleware
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware

from app.handlers import commands, text_messages, callbacks, documents, expenses, clients, bank, settings, mini_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Business OS Telegram Bot...")
    
    # Initialize Redis client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=False,
    )
    
    # Initialize bot and dispatcher with Redis storage for FSM
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    
    # Register middlewares (order matters: logging → rate limit → auth)
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware(redis_client=redis_client))
    dp.message.middleware(AuthMiddleware(redis_client=redis_client))
    
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(AuthMiddleware(redis_client=redis_client))
    
    # Register routers (order matters: specific handlers first, text_messages last)
    dp.include_router(commands.router)
    dp.include_router(documents.router)
    dp.include_router(expenses.router)
    dp.include_router(clients.router)
    dp.include_router(bank.router)
    dp.include_router(settings.router)
    dp.include_router(mini_app.router)
    dp.include_router(callbacks.router)
    dp.include_router(text_messages.router)  # Must be last to catch all text
    
    # Webhook or Polling
    if settings.WEBHOOK_URL:
        logger.info(f"Setting up webhook at {settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}")
        await bot.set_webhook(
            url=f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}",
            secret_token=settings.WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query"],
        )
        
        # Start aiohttp server for webhook (MVP: simple polling is default)
        from aiohttp import web
        
        async def handle_webhook(request: web.Request) -> web.Response:
            token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if settings.WEBHOOK_SECRET and token != settings.WEBHOOK_SECRET:
                return web.Response(status=401)
            
            update = await request.json()
            await dp.feed_webhook_update(bot, update)
            return web.Response(status=200)
        
        app = web.Application()
        app.router.add_post(settings.WEBHOOK_PATH, handle_webhook)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        
        logger.info("Webhook server started on port 8080")
        await asyncio.Event().wait()
    else:
        logger.info("Starting polling...")
        await bot.delete_webhook()
        await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
