"""Tests for payment operations."""
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.models import Payment
from app.schemas import PaymentCreate


@pytest.mark.asyncio
class TestPaymentCreation:
    async def test_create_payment(self, db_session):
        data = PaymentCreate(
            user_id=1,
            amount=Decimal("25000.00"),
            date=datetime.now(timezone.utc),
            description="Тестовый платеж",
            payment_type="income",
        )
        payment = Payment(**data.model_dump())
        db_session.add(payment)
        await db_session.flush()
        await db_session.refresh(payment)

        assert payment.id is not None
        assert payment.amount == Decimal("25000.00")
        assert payment.payment_type == "income"
        assert payment.currency == "RUB"
        assert payment.is_tax_calculated is False

    async def test_create_payment_expense(self, db_session):
        data = PaymentCreate(
            user_id=1,
            amount=Decimal("5000.00"),
            date=datetime.now(timezone.utc),
            description="Аренда",
            payment_type="expense",
            category="rent",
        )
        payment = Payment(**data.model_dump())
        db_session.add(payment)
        await db_session.flush()
        await db_session.refresh(payment)

        assert payment.payment_type == "expense"
        assert payment.category == "rent"

    async def test_payment_amount_must_be_positive(self, db_session):
        # SQLAlchemy check constraint will catch this at DB level
        # Here we test schema validation
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreate(
                user_id=1,
                amount=Decimal("-100"),
                date=datetime.now(timezone.utc),
            )
        assert "amount" in str(exc_info.value)

    async def test_payment_with_client(self, db_session):
        # Create a client first
        from app.models import Client
        client = Client(user_id=1, name="Клиент для платежа")
        db_session.add(client)
        await db_session.flush()
        await db_session.refresh(client)

        data = PaymentCreate(
            user_id=1,
            client_id=client.id,
            amount=Decimal("10000.00"),
            date=datetime.now(timezone.utc),
            description="Оплата от клиента",
        )
        payment = Payment(**data.model_dump())
        db_session.add(payment)
        await db_session.flush()
        await db_session.refresh(payment)

        assert payment.client_id == client.id

    async def test_payment_bank_fields(self, db_session):
        data = PaymentCreate(
            user_id=1,
            amount=Decimal("23000.00"),
            date=datetime.now(timezone.utc),
            description="Оплата за разработку",
            parsed_client_name="Иванов ИП",
            bank_transaction_id="tx-123",
            bank_name="tinkoff",
        )
        payment = Payment(**data.model_dump())
        db_session.add(payment)
        await db_session.flush()
        await db_session.refresh(payment)

        assert payment.parsed_client_name == "Иванов ИП"
        assert payment.bank_transaction_id == "tx-123"
        assert payment.bank_name == "tinkoff"
