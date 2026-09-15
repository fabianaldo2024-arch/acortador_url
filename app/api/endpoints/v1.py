"""
API Endpoints Router.
Rutas Principales de la API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


@router.get("/urls", tags=["URLs"])
async def list_urls(db: AsyncSession = Depends(get_db)):
    """
    List shortened URLs.
    Listar URLs acortadas.
    """
    return {"message": "Endpoints v1 active", "urls": []}
