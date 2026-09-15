"""
Configuration and shared fixtures for Pytest suite.
Configuración y accesorios compartidos para la suite de Pytest.
"""

from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app as fastapi_app
from app.core.database import Base, get_db
import app.models.models  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a clean database session for each test function.
    Proporciona una sesión de base de datos limpia para cada función de prueba.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an HTTPX AsyncClient with overridden database dependency.
    Proporciona un cliente HTTP asíncrono con la dependencia de base de datos sobrescrita.
    """
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
