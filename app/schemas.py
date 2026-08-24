from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

# ====== AUTH SCHEMAS ======
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ====== URL SCHEMAS ======
class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    clicks: int
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class URLUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
