"""Analytics router (Pulse, revenue charts, etc.)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.db import get_db
from app.deps import get_current_user
from app.models import Payment, Client, Expense, Document, TaxCalculation, User
from app.schemas import PulseData, TopClient
from app.services.tax_service import TaxService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/pulse")
async def get_pulse(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PulseData:
    """Return the Pulse (business snapshot) for current user."""
    now = datetime.now(timezone.utc)
    period_label = now.strftime("%B %Y")
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Revenue (income payments this month)
    revenue_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), Decimal("0"))).where(
            Payment.user_id == current_user.id,
            Payment.payment_type == "income",
            Payment.date >= month_start,
        )
    )
    total_revenue = revenue_result.scalar() or Decimal("0")

    # Expenses this month
    expenses_result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), Decimal("0"))).where(
            Expense.user_id == current_user.id,
            Expense.date >= month_start,
        )
    )
    total_expenses = expenses_result.scalar() or Decimal("0")

    profit = total_revenue - total_expenses

    # Tax for current period
    period_str = now.strftime("%Y-%m")
    tax_result = await db.execute(
        select(TaxCalculation).where(
            TaxCalculation.user_id == current_user.id,
            TaxCalculation.period == period_str,
        )
    )
    tax = tax_result.scalar_one_or_none()
    tax_amount = tax.tax_amount if tax else Decimal("0")
    tax_deadline = tax.deadline.isoformat() if tax and tax.deadline else None
    tax_days_remaining = 0
    if tax and tax.deadline:
        tax_days_remaining = max(0, (tax.deadline - now.date()).days)

    # Clients stats
    new_clients_result = await db.execute(
        select(func.count()).select_from(Client).where(
            Client.user_id == current_user.id,
            Client.created_at >= month_start,
            Client.deleted_at.is_(None),
        )
    )
    new_clients_count = new_clients_result.scalar() or 0

    total_clients_result = await db.execute(
        select(func.count()).select_from(Client).where(
            Client.user_id == current_user.id,
            Client.deleted_at.is_(None),
        )
    )
    total_clients_count = total_clients_result.scalar() or 0

    # Repeat clients (clients with >1 payment this month)
    repeat_result = await db.execute(
        select(func.count(func.distinct(Payment.client_id))).where(
            Payment.user_id == current_user.id,
            Payment.payment_type == "income",
            Payment.date >= month_start,
        )
    )
    repeat_clients_count = repeat_result.scalar() or 0

    # Top client by revenue
    top_client_result = await db.execute(
        select(Client).where(
            Client.user_id == current_user.id,
            Client.deleted_at.is_(None),
        ).order_by(Client.total_revenue.desc()).limit(1)
    )
    top_client = top_client_result.scalar_one_or_none()
    top_client_data = None
    if top_client:
        top_client_data = TopClient(
            id=top_client.id,
            name=top_client.name,
            total_revenue=str(top_client.total_revenue),
        )

    # Documents created this month
    docs_result = await db.execute(
        select(func.count()).select_from(Document).where(
            Document.user_id == current_user.id,
            Document.created_at >= month_start,
        )
    )
    documents_created = docs_result.scalar() or 0

    # Average check
    avg_check = Decimal("0")
    if total_revenue > 0 and total_clients_count > 0:
        avg_check = (total_revenue / Decimal(str(total_clients_count))).quantize(Decimal("0.01"))

    # Revenue change (previous month)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    prev_revenue_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), Decimal("0"))).where(
            Payment.user_id == current_user.id,
            Payment.payment_type == "income",
            Payment.date >= prev_month_start,
            Payment.date < month_start,
        )
    )
    prev_revenue = prev_revenue_result.scalar() or Decimal("0")
    revenue_change_percent = 0
    if prev_revenue > 0:
        revenue_change_percent = int(((total_revenue - prev_revenue) / prev_revenue) * 100)

    return PulseData(
        period=period_label,
        total_revenue=str(total_revenue.quantize(Decimal("0.01"))),
        revenue_change_percent=revenue_change_percent,
        total_expenses=str(total_expenses.quantize(Decimal("0.01"))),
        profit=str(profit.quantize(Decimal("0.01"))),
        tax_amount=str(tax_amount.quantize(Decimal("0.01"))),
        tax_deadline=tax_deadline,
        tax_days_remaining=tax_days_remaining,
        new_clients_count=new_clients_count,
        repeat_clients_count=repeat_clients_count,
        total_clients_count=total_clients_count,
        top_client=top_client_data,
        documents_created=documents_created,
        average_check=str(avg_check),
        ai_insight="В августе традиционно спад активности. Рекомендуем активировать рассылку «спящим» клиентам.",
    )


@router.get("/revenue")
async def get_revenue_chart(
    period: str = "month",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return aggregated revenue data for charts."""
    return {"period": period, "data": []}
