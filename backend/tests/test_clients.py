"""Tests for client service."""
import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.models import Client, User
from app.schemas import ClientCreate
from app.services.client_service import ClientService


@pytest.mark.asyncio
class TestClientService:
    async def test_create_client(self, db_session):
        service = ClientService(db_session)
        data = ClientCreate(
            user_id=1,
            name="ООО Тестовая Компания",
            type="company",
            inn="1234567890",
            phone="+79990000000",
            email="test@test.ru",
            notes="Тестовый клиент",
        )
        client = await service.create(data)
        assert client.id is not None
        assert client.name == "ООО Тестовая Компания"
        assert client.type == "company"
        assert client.inn == "1234567890"
        assert client.total_revenue == Decimal("0")
        assert client.deals_count == 0
        assert client.auto_created is False
        assert client.source == "manual"

    async def test_get_by_id(self, db_session):
        service = ClientService(db_session)
        data = ClientCreate(user_id=1, name="Иванов ИП", type="ip")
        client = await service.create(data)
        await db_session.commit()

        found = await service.get_by_id(client.id, user_id=1)
        assert found is not None
        assert found.name == "Иванов ИП"

    async def test_get_by_id_wrong_user(self, db_session):
        service = ClientService(db_session)
        data = ClientCreate(user_id=1, name="Скрытый клиент")
        client = await service.create(data)
        await db_session.commit()

        found = await service.get_by_id(client.id, user_id=999)
        assert found is None

    async def test_list_clients(self, db_session):
        service = ClientService(db_session)
        for i in range(5):
            await service.create(ClientCreate(user_id=1, name=f"Клиент {i}"))
        await db_session.commit()

        items, total = await service.list_clients(user_id=1)
        assert total == 5
        assert len(items) == 5

    async def test_list_clients_with_search(self, db_session):
        service = ClientService(db_session)
        await service.create(ClientCreate(user_id=1, name="Альфа"))
        await service.create(ClientCreate(user_id=1, name="Бета"))
        await db_session.commit()

        items, total = await service.list_clients(user_id=1, search="Альф")
        assert total == 1
        assert items[0].name == "Альфа"

    async def test_update_client(self, db_session):
        service = ClientService(db_session)
        client = await service.create(ClientCreate(user_id=1, name="Старый"))
        await db_session.commit()

        from app.schemas import ClientUpdate
        updated = await service.update(client, ClientUpdate(name="Новый"))
        assert updated.name == "Новый"

    async def test_soft_delete(self, db_session):
        service = ClientService(db_session)
        client = await service.create(ClientCreate(user_id=1, name="На удаление"))
        await db_session.commit()

        await service.soft_delete(client)
        await db_session.commit()

        assert client.deleted_at is not None

    async def test_get_or_create_from_payment(self, db_session):
        service = ClientService(db_session)
        client = await service.get_or_create_from_payment(
            user_id=1, parsed_name="Авто Клиент", inn="123456789012"
        )
        await db_session.commit()

        assert client.name == "Авто Клиент"
        assert client.inn == "123456789012"
        assert client.auto_created is True
        assert client.source == "bank_payment"

        # Second call should return existing
        client2 = await service.get_or_create_from_payment(
            user_id=1, parsed_name="авто клиент"
        )
        assert client2.id == client.id
