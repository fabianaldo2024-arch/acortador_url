from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models import URL, User
from app.schemas import URLCreate
import secrets
import string
from typing import Optional, List

class URLService:
    @staticmethod
    async def create_short_url(
        db: AsyncSession,
        url_data: URLCreate,
        user_id: Optional[int] = None
    ) -> URL:
        """Crea una URL corta"""
        # Generar código único
        short_code = URLService._generate_short_code()
        
        # Verificar que no exista usando SELECT
        existing = await db.execute(select(URL).where(URL.short_code == short_code))
        while existing.scalar_one_or_none():
            short_code = URLService._generate_short_code()
            existing = await db.execute(select(URL).where(URL.short_code == short_code))
        
        new_url = URL(
            original_url=str(url_data.original_url),
            short_code=short_code,
            user_id=user_id,
            expires_at=url_data.expires_at
        )
        
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)
        return new_url
    
    @staticmethod
    async def get_url_by_code(db: AsyncSession, short_code: str) -> Optional[URL]:
        """Obtiene una URL por su código corto usando SELECT"""
        result = await db.execute(
            select(URL).where(
                and_(
                    URL.short_code == short_code,
                    URL.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def increment_clicks(db: AsyncSession, url_id: int):
        """Incrementa el contador de clics"""
        from sqlalchemy import update
        stmt = update(URL).where(URL.id == url_id).values(
            clicks=URL.clicks + 1,
            last_accessed=func.now()
        )
        await db.execute(stmt)
        await db.commit()
    
    @staticmethod
    async def get_user_urls(db: AsyncSession, user_id: int) -> List[URL]:
        """Obtiene todas las URLs de un usuario"""
        result = await db.execute(
            select(URL).where(URL.user_id == user_id).order_by(URL.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_urls(db: AsyncSession) -> List[URL]:
        """Obtiene todas las URLs (solo admin)"""
        result = await db.execute(select(URL).order_by(URL.created_at.desc()))
        return result.scalars().all()
    
    @staticmethod
    async def update_url_metadata(db: AsyncSession, url_id: int, title: str, description: str, image_url: str):
        """Actualiza la metadata de una URL"""
        from sqlalchemy import update
        stmt = update(URL).where(URL.id == url_id).values(
            title=title,
            description=description,
            image_url=image_url
        )
        await db.execute(stmt)
        await db.commit()
    
    @staticmethod
    def _generate_short_code(length: int = 6) -> str:
        """Genera un código corto aleatorio"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
