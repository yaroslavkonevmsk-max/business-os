"""SQLAlchemy models for Business OS."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import BYTEA, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    pass


class User(Base):
    """User model (registered via Telegram)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    inn: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    ogrn: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tax_regime: Mapped[Optional[str]] = mapped_column(
        String(20),
        CheckConstraint("tax_regime IN ('usn_income', 'usn_income_expense', 'npd', 'patent')"),
        nullable=True,
    )
    bank_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tariff: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("tariff IN ('free', 'basic', 'pro', 'business')"),
        default="free",
        server_default=text("'free'"),
    )
    tariff_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="user", lazy="selectin")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user", lazy="selectin")
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="user", lazy="selectin")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="user", lazy="selectin")
    tax_calculations: Mapped[List["TaxCalculation"]] = relationship(
        "TaxCalculation", back_populates="user", lazy="selectin"
    )
    bank_connections: Mapped[List["BankConnection"]] = relationship(
        "BankConnection", back_populates="user", lazy="selectin"
    )
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False, lazy="selectin"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", back_populates="user", lazy="selectin"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", lazy="selectin")

    __table_args__ = (
        Index("idx_users_telegram_id", "telegram_id"),
        Index("idx_users_tariff", "tariff"),
        Index("idx_users_inn", "inn", postgresql_where=text("inn IS NOT NULL")),
    )


class UserSettings(Base):
    """User preferences and notification settings."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
    morning_brief_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
    morning_brief_time: Mapped[time] = mapped_column(Time, default=time(9, 0), server_default=text("'09:00:00'"))
    tax_reminders_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
    language: Mapped[str] = mapped_column(String(10), default="ru", server_default=text("'ru'"))
    currency: Mapped[str] = mapped_column(String(3), default="RUB", server_default=text("'RUB'"))
    timezone: Mapped[str] = mapped_column(
        String(50), default="Europe/Moscow", server_default=text("'Europe/Moscow'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="settings")


class Client(Base):
    """Client / counterparty model."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(
        String(20),
        CheckConstraint("type IN ('individual', 'company', 'ip')"),
        nullable=True,
    )
    inn: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    deals_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    first_payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auto_created: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    source: Mapped[str] = mapped_column(String(20), default="manual", server_default=text("'manual'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="clients")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="client", lazy="selectin")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="client", lazy="selectin")

    __table_args__ = (
        Index("idx_clients_user_id", "user_id"),
        Index("idx_clients_name", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
        Index("idx_clients_inn", "inn", postgresql_where=text("inn IS NOT NULL")),
        Index("idx_clients_auto_created", "user_id", "auto_created"),
    )


class Payment(Base):
    """Payment / transaction model (income or expense from any source)."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    bank_connection_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("bank_connections.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB", server_default=text("'RUB'"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    parsed_client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payment_type: Mapped[str] = mapped_column(
        String(10),
        CheckConstraint("payment_type IN ('income', 'expense')"),
        default="income",
        server_default=text("'income'"),
    )
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    document_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    is_tax_calculated: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="payments")
    client: Mapped[Optional["Client"]] = relationship("Client", back_populates="payments")
    bank_connection: Mapped[Optional["BankConnection"]] = relationship(
        "BankConnection", back_populates="payments"
    )
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payments_amount_positive"),
        Index("idx_payments_user_id", "user_id"),
        Index(
            "idx_payments_client_id",
            "client_id",
            postgresql_where=text("client_id IS NOT NULL"),
        ),
        Index("idx_payments_date", "user_id", "date"),
        Index(
            "idx_payments_bank_tx",
            "bank_transaction_id",
            postgresql_where=text("bank_transaction_id IS NOT NULL"),
        ),
        Index("idx_payments_type", "user_id", "payment_type"),
    )


class Expense(Base):
    """Expense record (manual input or from bank)."""

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_manual_category: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_expenses_amount_positive"),
        Index("idx_expenses_user_id", "user_id"),
        Index("idx_expenses_date", "user_id", "date"),
        Index("idx_expenses_category", "user_id", "category"),
    )


class Document(Base):
    """Generated document (invoice, act, waybill, GPH contract, report)."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("type IN ('invoice', 'act', 'waybill', 'gph_contract', 'report')"),
        nullable=False,
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('draft', 'sent', 'paid', 'cancelled')"),
        default="draft",
        server_default=text("'draft'"),
    )
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True
    )
    items: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prepayment_percent: Mapped[Optional[int]] = mapped_column(
        Integer, CheckConstraint("prepayment_percent BETWEEN 0 AND 100"), nullable=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="documents")
    client: Mapped["Client"] = relationship("Client", back_populates="documents")
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="document", foreign_keys="Payment.document_id"
    )

    __table_args__ = (
        Index("idx_documents_user_id", "user_id"),
        Index("idx_documents_client_id", "client_id"),
        Index("idx_documents_type", "user_id", "type"),
        Index("idx_documents_date", "user_id", "date"),
        Index("idx_documents_number", "user_id", "number"),
        UniqueConstraint("user_id", "number", name="idx_documents_user_number"),
    )


class TaxCalculation(Base):
    """Tax calculation per period and regime."""

    __tablename__ = "tax_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tax_regime: Mapped[str] = mapped_column(String(20), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    total_income: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    total_expenses: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    tax_base: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default=text("0"), nullable=False
    )
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('pending', 'paid', 'overdue')"),
        default="pending",
        server_default=text("'pending'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="tax_calculations")

    __table_args__ = (
        UniqueConstraint("user_id", "period", "tax_regime", name="uq_tax_user_period_regime"),
        Index("idx_tax_user_period", "user_id", "period"),
        Index("idx_tax_status", "user_id", "status"),
        Index(
            "idx_tax_deadline",
            "user_id",
            "deadline",
            postgresql_where=text("status = 'pending'"),
        ),
    )


class BankConnection(Base):
    """Connected bank account (OAuth tokens)."""

    __tablename__ = "bank_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    bank_code: Mapped[str] = mapped_column(String(20), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    account_mask: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('active', 'expired', 'error')"),
        default="active",
        server_default=text("'active'"),
    )
    access_token_encrypted: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    refresh_token_encrypted: Mapped[Optional[bytes]] = mapped_column(BYTEA, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="bank_connections")
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="bank_connection"
    )

    __table_args__ = (
        Index("idx_bank_conn_user", "user_id"),
        Index("idx_bank_conn_status", "user_id", "status"),
        Index("idx_bank_conn_bank", "user_id", "bank_code"),
    )


class Subscription(Base):
    """User subscription / tariff record."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tariff: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('active', 'cancelled', 'expired')"),
        default="active",
        server_default=text("'active'"),
    )
    payment_provider: Mapped[str] = mapped_column(
        String(20), default="yookassa", server_default=text("'yookassa'")
    )
    payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB", server_default=text("'RUB'"))
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    __table_args__ = (
        Index("idx_subs_user", "user_id"),
        Index("idx_subs_period", "user_id", "period_end"),
    )


class AuditLog(Base):
    """Audit trail for security and compliance (152-FZ)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_user", "user_id", "created_at"),
        Index("idx_audit_action", "action", "created_at"),
    )
