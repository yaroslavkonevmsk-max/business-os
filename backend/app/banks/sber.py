"""Sber Bank API Adapter."""

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


class SberAdapter(BankAdapter):
    """Adapter for Sber Business API.

    Sber specifics:
    - Sandbox available for testing
    - Two-factor authentication
    - Rate limit: 100 requests/minute
    - OAuth 2.0 Authorization Code Flow
    """

    BASE_URL = "https://api.sberbank.ru"
    AUTH_URL = "https://api.sberbank.ru/v1/oauth/authorize"
    TOKEN_URL = "https://api.sberbank.ru/v1/oauth/token"

    def __init__(self):
        self.client_id = os.getenv("SBER_CLIENT_ID", "")
        self.client_secret = os.getenv("SBER_CLIENT_SECRET", "")
        self.webhook_secret = os.getenv("SBER_WEBHOOK_SECRET", "")
        self._rate_limit_remaining = 100
        self._rate_limit_reset = datetime.utcnow()

    async def get_auth_url(self, state: str, redirect_uri: str) -> str:
        """Generate Sber OAuth authorization URL."""
        if not self.client_id:
            raise RuntimeError("SBER_CLIENT_ID not configured")

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "read_accounts read_transactions",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        await self._check_rate_limit()

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
                await self._update_rate_limit(response)
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Sber token exchange failed: {response.status} {text}"
                    )
                data = await response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in", 3600),
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        await self._check_rate_limit()

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
                await self._update_rate_limit(response)
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Sber refresh failed: {response.status} {text}"
                    )
                data = await response.json()

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_in": data.get("expires_in", 3600),
        }

    async def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Fetch user accounts from Sber."""
        await self._check_rate_limit()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/v1/accounts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            ) as response:
                await self._update_rate_limit(response)
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(
                        f"Sber get_accounts failed: {response.status} {text}"
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
        """Fetch transactions for a given account and date range.

        Sber rate limit: 100 requests/minute. We handle pagination
        and respect the limit.
        """
        params = {
            "fromDate": from_date.strftime("%Y-%m-%d"),
            "toDate": to_date.strftime("%Y-%m-%d"),
            "page": 0,
            "size": 100,
        }

        transactions = []
        async with aiohttp.ClientSession() as session:
            while True:
                await self._check_rate_limit()

                async with session.get(
                    f"{self.BASE_URL}/v1/accounts/{account_id}/transactions",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                    params=params,
                ) as response:
                    await self._update_rate_limit(response)
                    if response.status == 429:
                        raise RuntimeError("rate_limit")
                    if response.status != 200:
                        text = await response.text()
                        raise RuntimeError(
                            f"Sber get_transactions failed: {response.status} {text}"
                        )
                    data = await response.json()

                batch = data.get("transactions", [])
                if not batch:
                    break

                for tx in batch:
                    transactions.append(self._parse_transaction(tx))

                params["page"] += 1
                if len(batch) < params["size"]:
                    break

        return transactions

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Sber webhook signature using HMAC-SHA256."""
        if not self.webhook_secret:
            return True

        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def map_transaction(self, raw_tx: Dict[str, Any]) -> PaymentCreate:
        """Map raw Sber transaction to PaymentCreate.

        Sber field mapping (analogous to Tinkoff with Sber-specific fields):
            operationId         -> bank_transaction_id
            amount              -> amount
            currency            -> currency
        operationDate       -> date
            paymentPurpose      -> description
            payerName           -> parsed_client_name
            payerInn            -> (used for client lookup)
            debitCreditSign     -> payment_type (DEBIT=income, CREDIT=expense)
        """
        sign = raw_tx.get("debitCreditSign", "DEBIT")
        payment_type = "income" if sign == "DEBIT" else "expense"

        amount_raw = raw_tx.get("amount", 0)
        amount = abs(Decimal(str(amount_raw)))

        date_str = raw_tx.get("operationDate", datetime.utcnow().isoformat())
        if isinstance(date_str, datetime):
            tx_date = date_str
        else:
            # Sber may use different date formats; try ISO first
            try:
                tx_date = datetime.fromisoformat(
                    date_str.replace("Z", "+00:00")
                )
            except ValueError:
                tx_date = datetime.strptime(date_str, "%Y-%m-%d")

        return PaymentCreate(
            amount=amount,
            currency=raw_tx.get("currency", "RUB"),
            date=tx_date,
            description=raw_tx.get("paymentPurpose"),
            parsed_client_name=raw_tx.get("payerName")
            or raw_tx.get("counterpartyName"),
            bank_transaction_id=str(
                raw_tx.get("operationId", raw_tx.get("id", ""))
            ),
            bank_name="sber",
            payment_type=payment_type,
            category=raw_tx.get("category"),
        )

    def _parse_transaction(self, raw: Dict[str, Any]) -> BankTransaction:
        """Parse raw Sber transaction into BankTransaction model."""
        sign = raw.get("debitCreditSign", "DEBIT")
        direction = "IN" if sign == "DEBIT" else "OUT"
        amount = abs(Decimal(str(raw.get("amount", 0))))

        date_str = raw.get("operationDate", datetime.utcnow().isoformat())
        if isinstance(date_str, datetime):
            tx_date = date_str
        else:
            try:
                tx_date = datetime.fromisoformat(
                    date_str.replace("Z", "+00:00")
                )
            except ValueError:
                tx_date = datetime.strptime(date_str, "%Y-%m-%d")

        return BankTransaction(
            id=str(raw.get("operationId", raw.get("id", ""))),
            amount=amount,
            currency=raw.get("currency", "RUB"),
            date=tx_date,
            description=raw.get("paymentPurpose")
            or raw.get("description"),
            counterparty_name=raw.get("payerName")
            or raw.get("counterpartyName"),
            counterparty_inn=raw.get("payerInn")
            or raw.get("counterpartyInn"),
            direction=direction,
            account_id=str(raw.get("accountId", "")),
            category=raw.get("category"),
        )

    async def _check_rate_limit(self) -> None:
        """Raise if rate limit is exhausted."""
        if datetime.utcnow() < self._rate_limit_reset:
            if self._rate_limit_remaining <= 0:
                raise RuntimeError("rate_limit")

    async def _update_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        """Update internal rate limit counters from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
        if reset is not None:
            self._rate_limit_reset = datetime.fromtimestamp(int(reset))
        else:
            self._rate_limit_remaining -= 1

    @staticmethod
    def _mask_account(account_number: Optional[str]) -> Optional[str]:
        """Mask account number to ****1234 format."""
        if not account_number or len(account_number) < 4:
            return None
        return f"****{account_number[-4:]}"
