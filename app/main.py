"""
Application Entrypoint with FastAPI + NiceGUI.
Punto de Entrada Principal integrando FastAPI y NiceGUI.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from nicegui import ui

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.api.endpoints import router
from app.models.models import URL
from app.ui.pages import init_ui

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialization completed.")
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Endpoint de Salud
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Incluir Endpoints REST
app.include_router(router, prefix="/api")

# Redirección Dinámica de URLs Acortadas
@app.get("/{short_code}", tags=["Redirection"])
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url_entry = result.scalar_one_or_none()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL acortada no encontrada")

    url_entry.clicks += 1
    await db.commit()
    return RedirectResponse(url=url_entry.original_url)

# Inicializar Vistas de NiceGUI en Python
init_ui()

# Montar NiceGUI sobre FastAPI
ui.run_with(
    app,
    storage_secret=settings.SECRET_KEY,
    mount_path="/"
)
