"""Payments router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.deps import get_current_user
from app.models import Payment, User
from app.schemas import PaymentCreate, PaymentListResponse, PaymentResponse, PaymentUpdate

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentListResponse:
    """List payments for current user."""
    result = await db.execute(
        select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.date.desc())
    )
    items = result.scalars().all()
    count_result = await db.execute(
        select(func.count()).select_from(Payment).where(Payment.user_id == current_user.id)
    )
    total = count_result.scalar() or 0
    return PaymentListResponse(
        total=total,
        items=[PaymentResponse.model_validate(p) for p in items],
    )


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Create a new payment."""
    data.user_id = current_user.id
    payment = Payment(**data.model_dump(exclude_unset=True))
    db.add(payment)
    await db.flush()
    await db.refresh(payment)
    await db.commit()
    return PaymentResponse.model_validate(payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Get a single payment."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id, Payment.user_id == current_user.id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Update a payment."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id, Payment.user_id == current_user.id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)
    await db.flush()
    await db.refresh(payment)
    await db.commit()
    return PaymentResponse.model_validate(payment)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a payment."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id, Payment.user_id == current_user.id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    await db.delete(payment)
    await db.commit()


@router.post("/bank-webhook/{bank_code}", status_code=status.HTTP_200_OK)
async def bank_webhook(
    bank_code: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Receive bank webhook (Tinkoff / Sber)."""
    # Placeholder for bank webhook processing.
    # In production, verify signature, create payment, auto-create client, recalculate tax.
    # The actual implementation lives in Bank Integration module.
    return {"status": "received", "bank_code": bank_code}
