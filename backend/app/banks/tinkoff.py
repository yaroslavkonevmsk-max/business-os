"""Tinkoff Bank API Adapter."""

import hashlib
import hmac
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp

from backend.app.banks.adapter import (
    BankAccount,
    BankAdapter,
    BankTransaction,
    PaymentCreate,
)


class TinkoffAdapter(BankAdapter):
    """Adapter for Tinkoff (Т-Банк) OpenAPI."""

    BASE_URL = "https://api.tinkoff.ru"
    AUTH_URL = "https://api.tinkoff.ru/auth/oauth/authorize"
    TOKEN_URL = "https://api.tinkoff.ru/auth/oauth/token"

    def __init__(self):
        self.client_id = os.getenv("TINKOFF_CLIENT_ID", "")
        self.client_secret = os.getenv("TINKOFF_CLIENT_SECRET", "")
        self.webhook_secret = os.getenv("TINKOFF_WEBHOOK_SECRET", "")

    async def get_auth_url(self, state: str, redirect_uri: str) -> str:
        """Generate Tinkoff OAuth authorization URL."""
        if not self.client_id:
            raise RuntimeError("TINKOFF_CLIENT_ID not configured")

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "accounts transactions",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.TOKEN_URL, data=payload
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Tinkoff token exchange failed: {response.status} {text}"
                    )
                data = await response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in", 3600),
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.TOKEN_URL, data=payload
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Tinkoff refresh failed: {response.status} {text}"
                    )
                data = await response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_in": data.get("expires_in", 3600),
        }

    async def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Fetch user accounts from Tinkoff."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/api/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Tinkoff get_accounts failed: {response.status} {text}"
                    )
                data = await response.json()

        accounts = []
        for acc in data.get("accounts", []):
            accounts.append(
                BankAccount(
                    id=str(acc.get("id", "")),
                    account_number=acc.get("accountNumber"),
                    account_mask=self._mask_account(acc.get("accountNumber")),
                    currency=acc.get("currency", "RUB"),
                    balance=Decimal(str(acc.get("balance", 0)))
                    if acc.get("balance") is not None
                    else None,
                    name=acc.get("name"),
                )
            )
        return accounts

    async def get_transactions(
        self,
        access_token: str,
        account_id: str,
        from_date: datetime,
        to_date: datetime,
    ) -> List[BankTransaction]:
        """Fetch transactions for a given account and date range."""
        params = {
            "fromDate": from_date.isoformat(),
            "toDate": to_date.isoformat(),
            "limit": 100,
            "offset": 0,
        }

        transactions = []
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                    f"{self.BASE_URL}/api/v1/accounts/{account_id}/transactions",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                ) as response:
                    if response.status == 429:
                        raise RuntimeError("rate_limit")
                    if response.status != 200:
                        text = await response.text()
                        raise RuntimeError(
                            f"Tinkoff get_transactions failed: {response.status} {text}"
                        )
                    data = await response.json()

                batch = data.get("transactions", [])
                if not batch:
                    break

                for tx in batch:
                    transactions.append(self._parse_transaction(tx))

                params["offset"] += params["limit"]
                if len(batch) < params["limit"]:
                    break

        return transactions

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Tinkoff webhook signature using HMAC-SHA256.

        Args:
            payload: Raw request body.
            signature: Expected signature from X-Tinkoff-Signature header.

        Returns:
            True if signature matches.
        """
        if not self.webhook_secret:
            # In development, accept all if no secret configured
            return True

        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def map_transaction(self, raw_tx: Dict[str, Any]) -> PaymentCreate:
        """Map raw Tinkoff transaction to PaymentCreate per TZ 7.2.3.

        Mapping table:
            id                  -> bank_transaction_id
            amount              -> amount
            currency            -> currency
            date                -> date
            description         -> description
            counterpartyName    -> parsed_client_name
            counterpartyInn     -> (used for client lookup)
            direction           -> payment_type (IN=income, OUT=expense)
            accountId           -> (links to bank_connection)
        """
        direction = raw_tx.get("direction", "IN")
        payment_type = "income" if direction == "IN" else "expense"

        amount_raw = raw_tx.get("amount", 0)
        amount = abs(Decimal(str(amount_raw)))

        date_str = raw_tx.get("date", datetime.utcnow().isoformat())
        if isinstance(date_str, datetime):
            tx_date = date_str
        else:
            tx_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        return PaymentCreate(
            amount=amount,
            currency=raw_tx.get("currency", "RUB"),
            date=tx_date,
            description=raw_tx.get("description"),
            parsed_client_name=raw_tx.get("counterpartyName"),
            bank_transaction_id=str(raw_tx.get("transactionId", raw_tx.get("id", ""))),
            bank_name="tinkoff",
            payment_type=payment_type,
            category=raw_tx.get("category"),
        )

    def _parse_transaction(self, raw: Dict[str, Any]) -> BankTransaction:
        """Parse raw Tinkoff transaction into BankTransaction model."""
        direction = raw.get("direction", "IN")
        amount = abs(Decimal(str(raw.get("amount", 0))))
        date_str = raw.get("date", datetime.utcnow().isoformat())
        if isinstance(date_str, datetime):
            tx_date = date_str
        else:
            tx_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        return BankTransaction(
            id=str(raw.get("id", "")),
            amount=amount,
            currency=raw.get("currency", "RUB"),
            date=tx_date,
            description=raw.get("description"),
            counterparty_name=raw.get("counterpartyName"),
            counterparty_inn=raw.get("counterpartyInn"),
            direction=direction,
            account_id=str(raw.get("accountId", "")),
            category=raw.get("category"),
        )

    @staticmethod
    def _mask_account(account_number: Optional[str]) -> Optional[str]:
        """Mask account number to ****1234 format."""
        if not account_number or len(account_number) < 4:
            return None
        return f"****{account_number[-4:]}"
