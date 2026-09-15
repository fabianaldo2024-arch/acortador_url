"""
Database Models definitions.
Definición de Modelos de Base de Datos.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    urls: Mapped[List["URL"]] = relationship("URL", back_populates="owner", cascade="all, delete-orphan")


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    owner: Mapped[Optional[User]] = relationship("User", back_populates="urls")
