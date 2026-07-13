"""Bank Service: orchestrates adapters, token management, and transaction sync."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.banks.adapter import BankAdapter, PaymentCreate
from backend.app.banks.crypto import TokenEncryption
from backend.app.banks.sber import SberAdapter
from backend.app.banks.tinkoff import TinkoffAdapter


class BankServiceError(Exception):
    """Base exception for bank service errors."""

    pass


class TokenExpiredError(BankServiceError):
    """Raised when bank token is expired and refresh failed."""

    pass


class RateLimitError(BankServiceError):
    """Raised when bank API rate limit is hit."""

    pass


class BankService:
    """High-level service for bank integration operations.

    Responsibilities:
    - Adapter registry and selection by bank_code
    - Token encryption/decryption
    - Transaction synchronization with retry logic
    - Webhook handling
    - Error mapping per TZ 7.6
    """

    ADAPTERS: Dict[str, BankAdapter] = {
        "tinkoff": TinkoffAdapter(),
        "sber": SberAdapter(),
    }

    def __init__(self, db: AsyncSession, token_encryption: Optional[TokenEncryption] = None):
        self.db = db
        self._crypto = token_encryption or TokenEncryption()

    def get_adapter(self, bank_code: str) -> BankAdapter:
        """Get adapter instance by bank code.

        Args:
            bank_code: "tinkoff" or "sber".

        Returns:
            BankAdapter instance.

        Raises:
            ValueError: If bank_code is not supported.
        """
        adapter = self.ADAPTERS.get(bank_code)
        if not adapter:
            raise ValueError(f"Unsupported bank: {bank_code}")
        return adapter

    # ------------------------------------------------------------------
    # Token encryption helpers
    # ------------------------------------------------------------------

    def encrypt_token(self, token: str) -> bytes:
        """Encrypt a token string for DB storage."""
        return self._crypto.encrypt(token)

    def decrypt_token(self, ciphertext: bytes) -> str:
        """Decrypt token bytes from DB storage."""
        return self._crypto.decrypt(ciphertext)

    # ------------------------------------------------------------------
    # OAuth helpers
    # ------------------------------------------------------------------

    async def get_auth_url(self, bank_code: str, state: str, redirect_uri: str) -> str:
        """Generate OAuth authorization URL for the given bank.

        Args:
            bank_code: Bank identifier (e.g., "tinkoff").
            state: UUID state token for CSRF protection.
            redirect_uri: Application callback URL.

        Returns:
            Authorization URL to redirect user to.
        """
        adapter = self.get_adapter(bank_code)
        return await adapter.get_auth_url(state, redirect_uri)

    async def exchange_code(
        self, bank_code: str, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access tokens.

        Args:
            bank_code: Bank identifier.
            code: Authorization code from bank callback.
            redirect_uri: Same redirect URI used in auth request.

        Returns:
            Dict with access_token, refresh_token, expires_in.
        """
        adapter = self.get_adapter(bank_code)
        return await adapter.exchange_code(code, redirect_uri)

    async def refresh_token(self, bank_code: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token for a given bank.

        Args:
            bank_code: Bank identifier.
            refresh_token: Stored refresh token.

        Returns:
            Dict with new access_token, refresh_token, expires_in.
        """
        adapter = self.get_adapter(bank_code)
        return await adapter.refresh_token(refresh_token)

    # ------------------------------------------------------------------
    # Transaction synchronization
    # ------------------------------------------------------------------

    async def sync_transactions(
        self,
        bank_connection_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[PaymentCreate]:
        """Synchronize transactions for a bank connection.

        Steps per TZ 7.2:
        1. Load bank_connection from DB.
        2. Decrypt access_token.
        3. Check token expiration; refresh if needed.
        4. Fetch accounts.
        5. For each account, fetch transactions in date range.
        6. Map each raw transaction to PaymentCreate.

        Args:
            bank_connection_id: Primary key of bank_connections row.
            from_date: Start of sync range (default: 30 days ago).
            to_date: End of sync range (default: now).

        Returns:
            List of PaymentCreate objects ready for persistence.

        Raises:
            TokenExpiredError: If token refresh fails.
            RateLimitError: If bank API rate limit is hit.
            BankServiceError: For other bank API errors.
        """
        from backend.app.models import BankConnection

        conn = await self.db.get(BankConnection, bank_connection_id)
        if not conn:
            raise BankServiceError(
                f"BankConnection {bank_connection_id} not found"
            )

        adapter = self.get_adapter(conn.bank_code)

        # Decrypt access token
        access_token = self.decrypt_token(bytes(conn.access_token_encrypted))

        # Check expiration and refresh if needed
        if conn.token_expires_at and conn.token_expires_at < datetime.now(timezone.utc):
            if not conn.refresh_token_encrypted:
                raise TokenExpiredError(
                    f"Token expired for connection {bank_connection_id} and no refresh token"
                )
            refresh_tok = self.decrypt_token(bytes(conn.refresh_token_encrypted))
            try:
                token_data = await adapter.refresh_token(refresh_tok)
            except RuntimeError as exc:
                raise TokenExpiredError(f"Token refresh failed: {exc}") from exc

            # Update connection with new tokens
            access_token = token_data["access_token"]
            conn.access_token_encrypted = self.encrypt_token(access_token)
            if token_data.get("refresh_token"):
                conn.refresh_token_encrypted = self.encrypt_token(
                    token_data["refresh_token"]
                )
            expires_in = token_data.get("expires_in", 3600)
            conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in
            )
            conn.status = "active"
            conn.last_sync_error = None
            await self.db.commit()

        # Date range defaults
        if to_date is None:
            to_date = datetime.now(timezone.utc)
        if from_date is None:
            from_date = to_date - timedelta(days=30)

        # Fetch accounts
        try:
            accounts = await adapter.get_accounts(access_token)
        except RuntimeError as exc:
            error_msg = str(exc).lower()
            if "rate_limit" in error_msg:
                raise RateLimitError(f"{conn.bank_code} rate limit: {exc}") from exc
            raise BankServiceError(f"{conn.bank_code} API error: {exc}") from exc

        # Fetch transactions for each account
        all_payments: List[PaymentCreate] = []
        for account in accounts:
            try:
                raw_txs = await adapter.get_transactions(
                    access_token, account.id, from_date, to_date
                )
            except RuntimeError as exc:
                error_msg = str(exc).lower()
                if "rate_limit" in error_msg:
                    raise RateLimitError(
                        f"{conn.bank_code} rate limit during sync: {exc}"
                    ) from exc
                raise BankServiceError(
                    f"{conn.bank_code} transaction fetch error: {exc}"
                ) from exc

            for raw_tx in raw_txs:
                payment = adapter.map_transaction(raw_tx.model_dump())
                all_payments.append(payment)

        # Update last_sync_at
        conn.last_sync_at = datetime.now(timezone.utc)
        conn.status = "active"
        conn.last_sync_error = None
        await self.db.commit()

        return all_payments

    # ------------------------------------------------------------------
    # Webhook handling
    # ------------------------------------------------------------------

    def verify_webhook(
        self, bank_code: str, payload: bytes, signature: str
    ) -> bool:
        """Verify incoming webhook signature.

        Args:
            bank_code: Source bank (e.g., "tinkoff").
            payload: Raw request body.
            signature: Signature from header.

        Returns:
            True if signature is valid.
        """
        adapter = self.get_adapter(bank_code)
        return adapter.verify_webhook_signature(payload, signature)

    def map_webhook_transaction(
        self, bank_code: str, payload: Dict[str, Any]
    ) -> PaymentCreate:
        """Map a webhook payload to PaymentCreate.

        Args:
            bank_code: Source bank.
            payload: Parsed JSON body from webhook.

        Returns:
            PaymentCreate ready for persistence.
        """
        adapter = self.get_adapter(bank_code)
        return adapter.map_transaction(payload)

    # ------------------------------------------------------------------
    # Error handling helpers (TZ 7.6)
    # ------------------------------------------------------------------

    @staticmethod
    def classify_error(error: Exception) -> tuple[str, int, bool]:
        """Classify a bank API error for retry decisions.

        Returns:
            Tuple of (error_type, retry_seconds, should_retry).
        """
        msg = str(error).lower()
        if "rate_limit" in msg or "429" in msg:
            return "rate_limit", 60, True
        if "token expired" in msg or "401" in msg:
            return "token_expired", 0, False  # handled by refresh, not retry
        if "invalid account" in msg or "404" in msg:
            return "invalid_account", 0, False
        if "timeout" in msg or "connection" in msg or "api down" in msg:
            return "bank_down", 300, True
        return "unknown", 0, False
