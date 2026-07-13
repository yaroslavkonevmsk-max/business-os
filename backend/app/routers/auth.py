"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import AuthResponse, TelegramAuthRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(
    payload: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Validate Telegram initData and return JWT."""
    service = AuthService()
    try:
        user = await service.authenticate_or_register(db, payload.init_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    access_token = service.create_access_token(user.id)
    from app.schemas import UserResponse
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )
