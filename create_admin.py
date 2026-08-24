import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.auth import get_password_hash
from app.config import settings

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        admin = User(
            email="admin@admin.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("✅ Usuario admin creado: admin@admin.com / admin123")

if __name__ == "__main__":
    asyncio.run(create_admin())
