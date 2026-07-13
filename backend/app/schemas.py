"""Pydantic v2 schemas for all models."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Shared / Base
# ---------------------------------------------------------------------------
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseSchema):
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class UserCreate(BaseSchema):
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    company_name: Optional[str] = None
    tax_regime: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    inn: Optional[str] = None
    ogrn: Optional[str] = None
    company_name: Optional[str] = None
    tax_regime: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    tariff: Optional[str] = None
    tariff_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserResponse(BaseSchema):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    inn: Optional[str]
    ogrn: Optional[str]
    company_name: Optional[str]
    tax_regime: Optional[str]
    bank_details: Optional[Dict[str, Any]]
    tariff: str
    tariff_expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserMeResponse(UserResponse):
    settings: Optional["UserSettingsResponse"] = None


# ---------------------------------------------------------------------------
# UserSettings
# ---------------------------------------------------------------------------
class UserSettingsCreate(BaseSchema):
    user_id: int
    notifications_enabled: bool = True
    morning_brief_enabled: bool = True
    morning_brief_time: time = Field(default_factory=lambda: time(9, 0))
    tax_reminders_enabled: bool = True
    language: str = "ru"
    currency: str = "RUB"
    timezone: str = "Europe/Moscow"


class UserSettingsUpdate(BaseSchema):
    notifications_enabled: Optional[bool] = None
    morning_brief_enabled: Optional[bool] = None
    morning_brief_time: Optional[time] = None
    tax_reminders_enabled: Optional[bool] = None
    language: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None


class UserSettingsResponse(BaseSchema):
    id: int
    user_id: int
    notifications_enabled: bool
    morning_brief_enabled: bool
    morning_brief_time: time
    tax_reminders_enabled: bool
    language: str
    currency: str
    timezone: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------
class ClientCreate(BaseSchema):
    user_id: int
    name: str
    type: Optional[str] = None
    inn: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    source: str = "manual"

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) not in (10, 12):
            raise ValueError("ИНН должен содержать 10 или 12 цифр")
        return v


class ClientUpdate(BaseSchema):
    name: Optional[str] = None
    type: Optional[str] = None
    inn: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) not in (10, 12):
            raise ValueError("ИНН должен содержать 10 или 12 цифр")
        return v


class ClientResponse(BaseSchema):
    id: int
    user_id: int
    name: str
    type: Optional[str]
    inn: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    total_revenue: Decimal
    deals_count: int
    first_payment_date: Optional[date]
    last_payment_date: Optional[date]
    notes: Optional[str]
    auto_created: bool
    source: str
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseSchema):
    total: int
    items: List[ClientResponse]


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentCreate(BaseSchema):
    user_id: int
    client_id: Optional[int] = None
    bank_connection_id: Optional[int] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = "RUB"
    date: datetime
    description: Optional[str] = None
    parsed_client_name: Optional[str] = None
    bank_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    payment_type: str = "income"
    category: Optional[str] = None
    document_id: Optional[int] = None

    @field_validator("payment_type")
    @classmethod
    def validate_payment_type(cls, v: str) -> str:
        if v not in ("income", "expense"):
            raise ValueError("payment_type must be 'income' or 'expense'")
        return v


class PaymentUpdate(BaseSchema):
    client_id: Optional[int] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    date: Optional[datetime] = None
    description: Optional[str] = None
    category: Optional[str] = None
    document_id: Optional[int] = None
    is_tax_calculated: Optional[bool] = None


class PaymentResponse(BaseSchema):
    id: int
    user_id: int
    client_id: Optional[int]
    bank_connection_id: Optional[int]
    amount: Decimal
    currency: str
    date: datetime
    description: Optional[str]
    parsed_client_name: Optional[str]
    bank_transaction_id: Optional[str]
    bank_name: Optional[str]
    payment_type: str
    category: Optional[str]
    document_id: Optional[int]
    is_tax_calculated: bool
    created_at: datetime
    updated_at: datetime


class PaymentListResponse(BaseSchema):
    total: int
    items: List[PaymentResponse]


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------
class ExpenseCreate(BaseSchema):
    user_id: int
    amount: Decimal = Field(..., gt=0)
    date: datetime
    category: str
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    ai_category: Optional[str] = None
    is_manual_category: bool = True


class ExpenseUpdate(BaseSchema):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    date: Optional[datetime] = None
    category: Optional[str] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    ai_category: Optional[str] = None
    is_manual_category: Optional[bool] = None


class ExpenseResponse(BaseSchema):
    id: int
    user_id: int
    amount: Decimal
    date: datetime
    category: str
    description: Optional[str]
    receipt_url: Optional[str]
    ai_category: Optional[str]
    is_manual_category: bool
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseSchema):
    total: int
    items: List[ExpenseResponse]


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------
class DocumentItem(BaseSchema):
    name: str
    quantity: Decimal
    unit: str
    price: Decimal
    total: Decimal


class DocumentCreate(BaseSchema):
    user_id: int
    client_id: int
    type: str
    number: str
    total_amount: Decimal
    date: date
    items: List[DocumentItem]
    due_date: Optional[date] = None
    notes: Optional[str] = None
    prepayment_percent: Optional[int] = Field(default=None, ge=0, le=100)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("invoice", "act", "waybill", "gph_contract", "report"):
            raise ValueError("Invalid document type")
        return v


class DocumentUpdate(BaseSchema):
    number: Optional[str] = None
    total_amount: Optional[Decimal] = None
    date: Optional[date] = None
    status: Optional[str] = None
    items: Optional[List[DocumentItem]] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    prepayment_percent: Optional[int] = Field(default=None, ge=0, le=100)
    sent_at: Optional[datetime] = None
    sent_method: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("draft", "sent", "paid", "cancelled"):
            raise ValueError("Invalid status")
        return v


class DocumentResponse(BaseSchema):
    id: int
    user_id: int
    client_id: int
    type: str
    number: str
    total_amount: Decimal
    date: date
    status: str
    file_url: Optional[str]
    file_size: Optional[int]
    file_hash: Optional[str]
    payment_id: Optional[int]
    items: List[DocumentItem]
    due_date: Optional[date]
    notes: Optional[str]
    prepayment_percent: Optional[int]
    sent_at: Optional[datetime]
    sent_method: Optional[str]
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseSchema):
    total: int
    items: List[DocumentResponse]


# ---------------------------------------------------------------------------
# TaxCalculation
# ---------------------------------------------------------------------------
class TaxCalculationCreate(BaseSchema):
    user_id: int
    tax_regime: str
    period: str  # YYYY-MM
    total_income: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    tax_base: Decimal = Decimal("0")
    tax_rate: Decimal
    tax_amount: Decimal = Decimal("0")
    paid_amount: Decimal = Decimal("0")
    remaining_amount: Decimal = Decimal("0")
    deadline: Optional[date] = None
    status: str = "pending"


class TaxCalculationUpdate(BaseSchema):
    total_income: Optional[Decimal] = None
    total_expenses: Optional[Decimal] = None
    tax_base: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    remaining_amount: Optional[Decimal] = None
    deadline: Optional[date] = None
    status: Optional[str] = None


class TaxCalculationResponse(BaseSchema):
    id: int
    user_id: int
    tax_regime: str
    period: str
    total_income: Decimal
    total_expenses: Decimal
    tax_base: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    deadline: Optional[date]
    status: str
    created_at: datetime
    updated_at: datetime


class TaxCalculationListResponse(BaseSchema):
    total: int
    items: List[TaxCalculationResponse]


# ---------------------------------------------------------------------------
# BankConnection
# ---------------------------------------------------------------------------
class BankConnectionCreate(BaseSchema):
    user_id: int
    bank_code: str
    bank_name: str
    account_number: Optional[str] = None
    account_mask: Optional[str] = None
    access_token_encrypted: bytes
    refresh_token_encrypted: Optional[bytes] = None
    token_expires_at: Optional[datetime] = None


class BankConnectionUpdate(BaseSchema):
    account_number: Optional[str] = None
    account_mask: Optional[str] = None
    status: Optional[str] = None
    access_token_encrypted: Optional[bytes] = None
    refresh_token_encrypted: Optional[bytes] = None
    token_expires_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    last_sync_error: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("active", "expired", "error"):
            raise ValueError("Invalid status")
        return v


class BankConnectionResponse(BaseSchema):
    id: int
    user_id: int
    bank_code: str
    bank_name: str
    account_number: Optional[str]
    account_mask: Optional[str]
    status: str
    token_expires_at: Optional[datetime]
    last_sync_at: Optional[datetime]
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime


class BankConnectionListResponse(BaseSchema):
    total: int
    items: List[BankConnectionResponse]


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------
class SubscriptionCreate(BaseSchema):
    user_id: int
    tariff: str
    amount: Decimal
    currency: str = "RUB"
    period_start: date
    period_end: date
    auto_renew: bool = True
    payment_provider: str = "yookassa"
    payment_id: Optional[str] = None


class SubscriptionUpdate(BaseSchema):
    tariff: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[Decimal] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    auto_renew: Optional[bool] = None
    payment_id: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("active", "cancelled", "expired"):
            raise ValueError("Invalid status")
        return v


class SubscriptionResponse(BaseSchema):
    id: int
    user_id: int
    tariff: str
    status: str
    payment_provider: str
    payment_id: Optional[str]
    amount: Decimal
    currency: str
    period_start: date
    period_end: date
    auto_renew: bool
    created_at: datetime
    updated_at: datetime


class SubscriptionListResponse(BaseSchema):
    total: int
    items: List[SubscriptionResponse]


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------
class AuditLogCreate(BaseSchema):
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AuditLogResponse(BaseSchema):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime


class AuditLogListResponse(BaseSchema):
    total: int
    items: List[AuditLogResponse]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class TelegramAuthRequest(BaseSchema):
    init_data: str


class AuthResponse(BaseSchema):
    access_token: str
    user: UserResponse


# ---------------------------------------------------------------------------
# Analytics / Pulse
# ---------------------------------------------------------------------------
class TopClient(BaseSchema):
    id: int
    name: str
    total_revenue: str


class PulseData(BaseSchema):
    period: str
    total_revenue: str
    revenue_change_percent: int
    total_expenses: str
    profit: str
    tax_amount: str
    tax_deadline: Optional[str]
    tax_days_remaining: int
    new_clients_count: int
    repeat_clients_count: int
    total_clients_count: int
    top_client: Optional[TopClient]
    documents_created: int
    average_check: str
    ai_insight: str


# ---------------------------------------------------------------------------
# Bank OAuth
# ---------------------------------------------------------------------------
class BankConnectRequest(BaseSchema):
    bank_code: str


class BankConnectResponse(BaseSchema):
    auth_url: str


class BankCallbackRequest(BaseSchema):
    code: str
    state: str


class BankCallbackResponse(BaseSchema):
    success: bool
    connection_id: int
    bank_name: str


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------
class TinkoffWebhookPayload(BaseSchema):
    accountId: str
    transactionId: str
    amount: Decimal
    currency: str = "RUB"
    date: datetime
    description: str
    direction: str
    counterpartyName: str
    counterpartyInn: Optional[str] = None


# Re-export for forward references
UserMeResponse.model_rebuild()
