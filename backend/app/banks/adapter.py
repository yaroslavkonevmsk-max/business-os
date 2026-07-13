"""Abstract Bank Adapter pattern."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class BankAccount(BaseModel):
    """Represents a bank account."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    account_number: Optional[str] = None
    account_mask: Optional[str] = None
    currency: str = "RUB"
    balance: Optional[Decimal] = None
    name: Optional[str] = None


class BankTransaction(BaseModel):
    """Represents a raw bank transaction."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    amount: Decimal
    currency: str = "RUB"
    date: datetime
    description: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_inn: Optional[str] = None
    direction: str  # "IN" or "OUT"
    account_id: Optional[str] = None
    category: Optional[str] = None


class PaymentCreate(BaseModel):
    """Mapped payment ready for creation in our system."""

    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    currency: str = "RUB"
    date: datetime
    description: Optional[str] = None
    parsed_client_name: Optional[str] = None
    bank_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    payment_type: str = "income"  # "income" or "expense"
    category: Optional[str] = None


class BankAdapter(ABC):
    """Abstract base class for bank API adapters."""

    BASE_URL: str = ""

    @abstractmethod
    async def get_auth_url(self, state: str, redirect_uri: str) -> str:
        """Generate OAuth authorization URL.

        Args:
            state: CSRF/state token (UUID).
            redirect_uri: Callback URL after authorization.

        Returns:
            Full authorization URL to redirect user to.
        """
        ...

    @abstractmethod
    async def exchange_code(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access tokens.

        Args:
            code: Authorization code from bank callback.
            redirect_uri: Same redirect URI used in auth request.

        Returns:
            Dict with at least: access_token, refresh_token, expires_in (seconds).
        """
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Stored refresh token.

        Returns:
            Dict with: access_token, refresh_token, expires_in.
        """
        ...

    @abstractmethod
    async def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Fetch list of accounts for the user.

        Args:
            access_token: Valid access token.

        Returns:
            List of BankAccount objects.
        """
        ...

    @abstractmethod
    async def get_transactions(
        self,
        access_token: str,
        account_id: str,
        from_date: datetime,
        to_date: datetime,
    ) -> List[BankTransaction]:
        """Fetch transactions for an account in a date range.

        Args:
            access_token: Valid access token.
            account_id: Bank account ID.
            from_date: Start date (inclusive).
            to_date: End date (inclusive).

        Returns:
            List of BankTransaction objects.
        """
        ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook payload signature.

        Args:
            payload: Raw request body bytes.
            signature: Signature from header (e.g., X-Tinkoff-Signature).

        Returns:
            True if signature is valid.
        """
        ...

    @abstractmethod
    def map_transaction(self, raw_tx: Dict[str, Any]) -> PaymentCreate:
        """Map raw bank transaction to our PaymentCreate model.

        Args:
            raw_tx: Raw transaction dict from bank API/webhook.

        Returns:
            PaymentCreate ready for persistence.
        """
        ...
