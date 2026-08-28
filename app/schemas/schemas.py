# app/schemas/schemas.py
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User ---
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

# --- URL ---
class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    expires_at: Optional[datetime] = None

class URLResponse(URLBase):
    id: int
    short_code: str
    clicks: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True