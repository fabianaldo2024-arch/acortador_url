from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    urls = relationship("URL", back_populates="user", cascade="all, delete-orphan")

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    clicks = Column(BigInteger, default=0)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="urls")
