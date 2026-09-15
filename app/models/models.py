"""
SQLAlchemy ORM Models.
Modelos ORM de SQLAlchemy.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class User(Base):
    """
    User model for authentication and management.
    Modelo de usuario para autenticación y gestión.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

class URL(Base):
    """
    URL mapping model for shortened links.
    Modelo de mapeo de URL para enlaces acortados.
    """
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
