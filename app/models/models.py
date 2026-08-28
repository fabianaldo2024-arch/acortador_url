# app/models/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

        # Nuevos campos para metadatos
    #title = Column(String(500), nullable=True)
    #description = Column(Text, nullable=True)
    #image = Column(String(500), nullable=True)
    
    urls = relationship("URL", back_populates="user")

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(50), unique=True, index=True, nullable=False)
    clicks = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    expires_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    user = relationship("User", back_populates="urls")
