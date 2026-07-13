"""Authentication service: Telegram initData → JWT."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Dict, Optional
from urllib.parse import parse_qs, unquote

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models import User, UserSettings
from app.schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handle Telegram WebApp initData validation and JWT issuance."""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.BOT_TOKEN

    def _check_signature(self, init_data: str) -> bool:
        """Verify Telegram WebApp initData signature."""
        if not self.bot_token:
            # Dev mode: accept without verification
            return True

        try:
            # Parse initData string
            parsed = parse_qs(init_data, keep_blank_values=True)
            hash_value = parsed.get("hash", [""])[0]
            if not hash_value:
                return False

            # Build data_check_string from sorted params excluding hash
            data_pairs = []
            for key, values in parsed.items():
                if key == "hash":
                    continue
                for value in values:
                    data_pairs.append(f"{key}={unquote(value)}")
            data_check_string = "\n".join(sorted(data_pairs))

            # Compute secret key from bot token
            secret_key = hmac.new(
                key=b"WebAppData",
                msg=self.bot_token.encode(),
                digestmod=hashlib.sha256,
            ).digest()

            # Verify signature
            expected_hash = hmac.new(
                key=secret_key,
                msg=data_check_string.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected_hash, hash_value)
        except Exception:
            return False

    def _parse_user_from_init_data(self, init_data: str) -> Dict:
        """Extract user JSON from initData."""
        parsed = parse_qs(init_data, keep_blank_values=True)
        user_json = parsed.get("user", ["{}"])[0]
        return json.loads(user_json)

    def create_access_token(self, user_id: int) -> str:
        """Create JWT access token."""
        to_encode = {"sub": str(user_id), "iat": int(time.time())}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    async def authenticate_or_register(
        self,
        db: AsyncSession,
        init_data: str,
    ) -> User:
        """Validate initData, register or return existing user."""
        if not self._check_signature(init_data):
            raise ValueError("Invalid Telegram initData signature")

        user_data = self._parse_user_from_init_data(init_data)
        telegram_id = int(user_data.get("id", 0))
        if not telegram_id:
            raise ValueError("No telegram_id in initData")

        # Check existing user
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if user is None:
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=user_data.get("username"),
                full_name=user_data.get("first_name", "") + " " + user_data.get("last_name", ""),
                is_active=True,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

            # Create default settings
            settings_obj = UserSettings(user_id=user.id)
            db.add(settings_obj)
            await db.flush()

            # Refresh user with settings
            await db.refresh(user)

        return user

    async def get_user_by_telegram_id(
        self, db: AsyncSession, telegram_id: int
    ) -> Optional[User]:
        """Get user by telegram_id."""
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()
