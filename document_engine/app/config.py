"""Document Engine configuration."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    # S3 / Selectel
    s3_endpoint: str = ""
    s3_bucket: str = "business-os-documents"
    s3_key: str = ""
    s3_secret: str = ""
    s3_region: str = "ru-1"
    s3_public_url: str = ""

    # LibreOffice
    libreoffice_path: str = "libreoffice"

    # Backend API
    backend_api_url: str = "http://backend:8000"
    backend_api_key: str = ""

    # Directories
    templates_dir: Path = Path(__file__).parent / "templates"
    temp_dir: Path = Path("/tmp/documents")

    # QR codes
    qr_enabled: bool = True
    yookassa_payment_base_url: str = "https://yookassa.ru/payments"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def broker_url(self) -> str:
        """Celery broker URL."""
        return self.redis_url

    @property
    def s3_client_config(self) -> dict:
        """Boto3 S3 client configuration."""
        config: dict = {
            "service_name": "s3",
            "aws_access_key_id": self.s3_key,
            "aws_secret_access_key": self.s3_secret,
            "region_name": self.s3_region,
        }
        if self.s3_endpoint:
            config["endpoint_url"] = self.s3_endpoint
        return config


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
