"""Application configuration."""
import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-32-chars-long!!"
    API_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/business_os"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram
    BOT_TOKEN: str = ""
    MINI_APP_URL: str = ""

    # YandexGPT
    YANDEXGPT_FOLDER_ID: str = ""
    YANDEXGPT_IAM_TOKEN: str = ""

    # Banks
    TINKOFF_CLIENT_ID: str = ""
    TINKOFF_CLIENT_SECRET: str = ""
    SBER_CLIENT_ID: str = ""
    SBER_CLIENT_SECRET: str = ""
    BANK_TOKEN_ENCRYPTION_KEY: str = ""

    # YooKassa
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    YOOKASSA_WEBHOOK_SECRET: str = ""

    # S3 / Selectel
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_KEY: str = ""
    S3_SECRET: str = ""
    S3_REGION: str = "ru-1"

    # Monitoring
    SENTRY_DSN: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url_async(self) -> str:
        """Return async database URL."""
        return self.DATABASE_URL


settings = Settings()
