"""Audit logging middleware."""
from __future__ import annotations

import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.db import AsyncSessionLocal
from app.models import AuditLog, User


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request to audit_log table."""

    def __init__(self, app, skip_paths: Optional[list] = None):
        super().__init__(app)
        self.skip_paths = set(skip_paths or ["/health", "/docs", "/openapi.json", "/redoc"])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if path in self.skip_paths:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Log async in background (fire-and-forget style via task)
        user_id: Optional[int] = None
        try:
            state_user = getattr(request.state, "user", None)
            if isinstance(state_user, User):
                user_id = state_user.id
        except Exception:
            pass

        # Don't block response; log in a separate task would be ideal,
        # but for simplicity we use a detached session here.
        try:
            async with AsyncSessionLocal() as db:
                log = AuditLog(
                    user_id=user_id,
                    action=f"{request.method} {path}",
                    entity_type="request",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    details={
                        "path": path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                    },
                )
                db.add(log)
                await db.commit()
        except Exception:
            # Audit logging should never break the app
            pass

        return response
