"""FastAPI dependencies."""
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import AsyncSessionLocal, get_db
from app.models import User
from app.schemas import UserResponse

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate JWT and return the current user."""
    token = None

    if credentials is not None:
        token = credentials.credentials
    else:
        # Try query param or cookie as fallback
        token = request.query_params.get("token") or request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Could not validate credentials") from exc

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    return user


async def get_current_user_response(
    user: User = Depends(get_current_user),
) -> UserResponse:
    """Return current user as Pydantic response model."""
    return UserResponse.model_validate(user)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Standalone DB session for contexts outside FastAPI DI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
