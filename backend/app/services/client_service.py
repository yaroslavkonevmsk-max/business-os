"""Client service with business logic and aggregation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Client, Payment
from app.schemas import ClientCreate, ClientUpdate
from app.services.tax_service import TaxService


class ClientService:
    """Business logic for client management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tax_service = TaxService()

    async def create(self, data: ClientCreate) -> Client:
        """Create a new client."""
        client = Client(
            user_id=data.user_id,
            name=data.name,
            type=data.type,
            inn=data.inn,
            phone=data.phone,
            email=data.email,
            notes=data.notes,
            source=data.source,
        )
        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)
        return client

    async def get_by_id(self, client_id: int, user_id: int) -> Optional[Client]:
        """Get client by ID scoped to user."""
        result = await self.db.execute(
            select(Client).where(Client.id == client_id, Client.user_id == user_id, Client.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_clients(
        self,
        user_id: int,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Client], int]:
        """List clients with optional search and pagination."""
        query = select(Client).where(Client.user_id == user_id, Client.deleted_at.is_(None))

        if search:
            query = query.where(Client.name.ilike(f"%{search}%"))

        # Count total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Paginate
        query = query.order_by(Client.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def update(self, client: Client, data: ClientUpdate) -> Client:
        """Update client fields."""
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(client, field, value)
        await self.db.flush()
        await self.db.refresh(client)
        return client

    async def soft_delete(self, client: Client) -> None:
        """Soft delete a client."""
        from datetime import datetime, timezone
        client.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def get_or_create_from_payment(
        self,
        user_id: int,
        parsed_name: str,
        inn: Optional[str] = None,
    ) -> Client:
        """Auto-create a client from a bank payment if not exists."""
        # Try to find existing client by name (case-insensitive) for this user
        result = await self.db.execute(
            select(Client).where(
                Client.user_id == user_id,
                Client.deleted_at.is_(None),
                func.lower(Client.name) == func.lower(parsed_name),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        # Create auto-created client
        client = Client(
            user_id=user_id,
            name=parsed_name,
            type="individual",
            inn=inn,
            auto_created=True,
            source="bank_payment",
        )
        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)
        return client
