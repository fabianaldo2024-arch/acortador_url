# create_tables.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app import models  # Importa tus modelos para que SQLAlchemy los reconozca

# --- IMPORTANTE: Asegúrate de que esta URL coincida con la de tu .env ---
# Si usas SQLite, debería ser algo como "sqlite+aiosqlite:///./url_shortener.db"
DATABASE_URL = "sqlite+aiosqlite:///./url_shortener.db"

async def create_tables():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Crea todas las tablas definidas en tus modelos
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas exitosamente.")

if __name__ == "__main__":
    asyncio.run(create_tables())