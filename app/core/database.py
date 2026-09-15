"""
Database connection and session management module.
Módulo de gestión de conexiones y sesiones de base de datos.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("acortador.database")

# Obtener URL de base de datos desde entorno o fallar a SQLite en memoria por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# Crear el motor asíncrono de SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Fabrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy declarative models.
    Clase base para modelos declarativos de SQLAlchemy.
    """
    pass

async def init_db() -> None:
    """
    Initialize database tables asynchronously.
    Inicializa las tablas de la base de datos de forma asíncrona.
    """
    # Importar modelos explícitamente para registrar metadatos antes de la creación
    import app.models.models  # noqa: F401
    
    async with engine.begin() as conn:
        logger.info("Creating database tables if they do not exist...")
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for FastAPI AsyncSession.
    Proveedor de dependencia para AsyncSession en FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as err:
            await session.rollback()
            logger.error(f"Database session error: {err}")
            raise
        finally:
            await session.close()
