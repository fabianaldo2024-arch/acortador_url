"""
FastAPI Main Application Entrypoint.
Punto de entrada principal de la aplicación FastAPI.
"""

import logging
import random
import string
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import init_db, get_db
from app.models.models import URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acortador")

@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager / Gestor del ciclo de vida de la aplicación."""
    logger.info("Initializing database tables...")
    await init_db()
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title="Acortador de URLs API",
    version="0.2.0",
    lifespan=lifespan
)

class URLCreateSchema(BaseModel):
    target_url: HttpUrl

class URLResponseSchema(BaseModel):
    short_code: str
    target_url: str

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Healthcheck endpoint / Endpoint de sanidad."""
    try:
        await db.execute(select(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as err:
        logger.error(f"Healthcheck failed: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )

@app.post("/api/v1/shorten", response_model=URLResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_short_url(
    payload: URLCreateSchema,
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Shorten target URL / Acorta una URL de destino."""
    chars = string.ascii_letters + string.digits
    short_code = "".join(random.choice(chars) for _ in range(6))
    
    target_url_str = str(payload.target_url)
    new_url = URL(target_url=target_url_str, short_code=short_code)
    
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)
    
    return {"short_code": new_url.short_code, "target_url": new_url.target_url}

@app.get("/{short_code}")
async def redirect_url(short_code: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Retrieve target URL from short code / Obtiene URL de destino por código."""
    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url_item = result.scalar_one_or_none()
    
    if not url_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    
    return {"target_url": url_item.target_url}
