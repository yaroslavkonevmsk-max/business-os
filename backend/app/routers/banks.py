"""Bank integration router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db import get_db
from app.deps import get_current_user
from app.models import BankConnection, User
from app.schemas import BankConnectRequest, BankConnectResponse, BankCallbackRequest, BankCallbackResponse

router = APIRouter(prefix="/banks", tags=["Banks"])


@router.post("/connect", response_model=BankConnectResponse)
async def connect_bank(
    data: BankConnectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankConnectResponse:
    """Start bank OAuth connection."""
    if data.bank_code == "tinkoff":
        import uuid
        state = str(uuid.uuid4())
        # In production, store state in Redis with TTL 10 min
        auth_url = (
            f"https://api.tinkoff.ru/auth/oauth/authorize?"
            f"client_id={settings.TINKOFF_CLIENT_ID}&"
            f"redirect_uri={settings.API_URL}/api/v1/banks/callback&"
            f"response_type=code&"
            f"state={state}&"
            f"scope=accounts+transactions"
        )
        return BankConnectResponse(auth_url=auth_url)
    elif data.bank_code == "sber":
        return BankConnectResponse(auth_url="https://developer.sber.ru/oauth/authorize")
    raise HTTPException(status_code=400, detail="Unsupported bank code")


@router.get("/callback")
async def bank_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> BankCallbackResponse:
    """Handle OAuth callback from bank."""
    # In production: verify state, exchange code for tokens, encrypt and store.
    # This is a stub that returns success for structural completeness.
    return BankCallbackResponse(success=True, connection_id=0, bank_name="Tinkoff")


@router.get("", response_model=list)
async def list_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    """List connected bank accounts."""
    result = await db.execute(
        select(BankConnection).where(BankConnection.user_id == current_user.id)
    )
    items = result.scalars().all()
    from app.schemas import BankConnectionResponse
    return [BankConnectionResponse.model_validate(i).model_dump() for i in items]


@router.delete("/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a bank connection."""
    result = await db.execute(
        select(BankConnection).where(
            BankConnection.id == connection_id,
            BankConnection.user_id == current_user.id,
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    await db.delete(conn)
    await db.commit()
