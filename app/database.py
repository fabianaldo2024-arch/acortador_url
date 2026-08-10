from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import os

# Detectar si es SQLite o PostgreSQL
is_sqlite = "sqlite" in settings.DATABASE_URL

# Configuración del engine según el tipo de base de datos
if is_sqlite:
    # SQLite - configuraciones básicas
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        future=True,
        connect_args={"check_same_thread": False}  # Necesario para SQLite
    )
else:
    # PostgreSQL - con pool de conexiones
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        future=True,
        pool_size=10,
        max_overflow=20
    )

# Crear session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Dependencia para obtener sesión de BD
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
