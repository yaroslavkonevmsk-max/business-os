"""Pytest configuration and fixtures."""
import os
import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Use a test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://app:app@localhost:5432/business_os_test",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
AsyncTestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def db_session():
    """Provide a database session for each test, rolling back after."""
    async with AsyncTestingSessionLocal() as session:
        async with session.begin():
            yield session
        await session.rollback()
