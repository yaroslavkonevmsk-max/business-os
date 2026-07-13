"""Celery application for the backend (document generation, bank sync, notifications)."""

from __future__ import annotations

import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_CELERY_URL", os.getenv("REDIS_URL", "redis://redis:6379/1"))

app = Celery(
    "business_os",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.services.tax_service",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
