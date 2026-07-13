from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token from @BotFather")
    API_URL: str = Field(default="http://backend:8000", description="Backend API base URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Webhook settings (optional, defaults to polling)
    WEBHOOK_URL: str | None = Field(default=None, description="Webhook base URL (e.g. https://bot.example.com)")
    WEBHOOK_PATH: str = Field(default="/webhook", description="Webhook path")
    WEBHOOK_SECRET: str | None = Field(default=None, description="Secret token for webhook verification")
    
    # Bot behavior
    RATE_LIMIT_SECONDS: int = Field(default=1, description="Rate limit per user in seconds")
    JWT_TTL_SECONDS: int = Field(default=3600, description="JWT cache TTL in Redis")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
