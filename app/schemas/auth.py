"""
Pydantic Schemas for Authentication.
Esquemas de Pydantic para Autenticación.
"""

from pydantic import BaseModel, EmailStr, Field

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password min 8 chars / Mínimo 8 caracteres")

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
