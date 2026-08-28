# app/services/url_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
import random
import string
from typing import Optional
from app.models import URL
from app.schemas import URLCreate

class URLService:
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """Genera un código corto aleatorio."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    async def create_short_url(
        db: AsyncSession,
        url_data: URLCreate,
        user_id: Optional[int] = None
    ) -> URL:
        """Crea una URL corta."""
        # Generar código único
        short_code = URLService.generate_short_code()
        existing = await db.execute(select(URL).where(URL.short_code == short_code))
        while existing.scalar_one_or_none():
            short_code = URLService.generate_short_code()
            existing = await db.execute(select(URL).where(URL.short_code == short_code))

        new_url = URL(
            original_url=str(url_data.original_url),
            short_code=short_code,
            user_id=user_id,
            clicks=0,
            is_active=True,
            created_at=datetime.utcnow(),
            expires_at=url_data.expires_at if hasattr(url_data, 'expires_at') else None
        )

        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)
        return new_url

    @staticmethod
    async def get_url_by_code(db: AsyncSession, short_code: str) -> Optional[URL]:
        """Obtiene una URL por su código corto."""
        result = await db.execute(
            select(URL).where(URL.short_code == short_code, URL.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_urls(db: AsyncSession, user_id: int) -> list[URL]:
        """Obtiene todas las URLs de un usuario."""
        result = await db.execute(
            select(URL).where(URL.user_id == user_id).order_by(URL.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_urls(db: AsyncSession) -> list[URL]:
        """Obtiene todas las URLs (para admin)."""
        result = await db.execute(
            select(URL).order_by(URL.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def increment_clicks(db: AsyncSession, url_id: int) -> None:
        """Incrementa el contador de clicks de una URL."""
        await db.execute(
            update(URL)
            .where(URL.id == url_id)
            .values(clicks=URL.clicks + 1)
        )
        await db.commit()

    @staticmethod
    async def deactivate_url(db: AsyncSession, url_id: int) -> None:
        """Desactiva una URL."""
        await db.execute(
            update(URL)
            .where(URL.id == url_id)
            .values(is_active=False)
        )
        await db.commit()

    @staticmethod
    async def update_url_metadata(
        db: AsyncSession,
        url_id: int,
        title: str,
        description: Optional[str] = None,
        image: Optional[str] = None
    ) -> Optional[URL]:
        """Actualiza los metadatos de una URL."""
        url = await db.get(URL, url_id)
        if url:
            url.title = title
            url.description = description
            url.image = image
            await db.commit()
            await db.refresh(url)
        return url