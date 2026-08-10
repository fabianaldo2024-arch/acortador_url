import asyncio
from app.database import engine, Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas creadas exitosamente en SQLite")

if __name__ == "__main__":
    asyncio.run(create_tables())
