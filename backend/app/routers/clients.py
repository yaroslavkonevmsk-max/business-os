"""Clients router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.deps import get_current_user
from app.models import Client, User
from app.schemas import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=ClientListResponse)
async def list_clients(
    page: int = 1,
    search: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientListResponse:
    """List clients with search and pagination."""
    service = ClientService(db)
    items, total = await service.list_clients(
        user_id=current_user.id,
        search=search or None,
        page=page,
    )
    return ClientListResponse(
        total=total,
        items=[ClientResponse.model_validate(c) for c in items],
    )


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Create a new client."""
    data.user_id = current_user.id
    service = ClientService(db)
    client = await service.create(data)
    await db.commit()
    return ClientResponse.model_validate(client)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Get a single client by ID."""
    service = ClientService(db)
    client = await service.get_by_id(client_id, current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientResponse:
    """Update a client."""
    service = ClientService(db)
    client = await service.get_by_id(client_id, current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    updated = await service.update(client, data)
    await db.commit()
    return ClientResponse.model_validate(updated)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Soft delete a client."""
    service = ClientService(db)
    client = await service.get_by_id(client_id, current_user.id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    await service.soft_delete(client)
    await db.commit()
