"""Taxes router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.deps import get_current_user
from app.models import TaxCalculation, User
from app.schemas import (
    TaxCalculationCreate,
    TaxCalculationListResponse,
    TaxCalculationResponse,
    TaxCalculationUpdate,
)
from app.services.tax_service import TaxService

router = APIRouter(prefix="/taxes", tags=["Taxes"])


@router.get("", response_model=TaxCalculationListResponse)
async def list_tax_calculations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaxCalculationListResponse:
    """List tax calculations for current user."""
    result = await db.execute(
        select(TaxCalculation)
        .where(TaxCalculation.user_id == current_user.id)
        .order_by(TaxCalculation.period.desc())
    )
    items = result.scalars().all()
    total = (
        await db.execute(
            select(func.count())
            .select_from(TaxCalculation)
            .where(TaxCalculation.user_id == current_user.id)
        )
    ).scalar() or 0
    return TaxCalculationListResponse(
        total=total,
        items=[TaxCalculationResponse.model_validate(t) for t in items],
    )


@router.post("", response_model=TaxCalculationResponse)
async def create_tax_calculation(
    data: TaxCalculationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaxCalculationResponse:
    """Create or recalculate tax for a period."""
    data.user_id = current_user.id
    tax_calc = TaxCalculation(**data.model_dump(exclude_unset=True))
    db.add(tax_calc)
    await db.flush()
    await db.refresh(tax_calc)
    await db.commit()
    return TaxCalculationResponse.model_validate(tax_calc)


@router.get("/current")
async def get_current_tax(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get current tax calculation for the active period."""
    from datetime import datetime, timezone
    period = datetime.now(timezone.utc).strftime("%Y-%m")
    result = await db.execute(
        select(TaxCalculation).where(
            TaxCalculation.user_id == current_user.id,
            TaxCalculation.period == period,
        )
    )
    tax = result.scalar_one_or_none()
    if not tax:
        return {"period": period, "tax_amount": "0.00", "status": "pending"}
    return TaxCalculationResponse.model_validate(tax).model_dump()


@router.get("/deadlines")
async def get_deadlines(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get upcoming tax deadlines."""
    service = TaxService()
    from datetime import datetime, timezone
    period = datetime.now(timezone.utc).strftime("%Y-%m")
    deadline = service.get_tax_deadline(period)
    return {"period": period, "deadline": deadline}


@router.get("/{tax_id}", response_model=TaxCalculationResponse)
async def get_tax_calculation(
    tax_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaxCalculationResponse:
    result = await db.execute(
        select(TaxCalculation).where(
            TaxCalculation.id == tax_id, TaxCalculation.user_id == current_user.id
        )
    )
    tax = result.scalar_one_or_none()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax calculation not found")
    return TaxCalculationResponse.model_validate(tax)
