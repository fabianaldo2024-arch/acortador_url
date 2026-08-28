from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Importaciones corregidas (usando app.core)
from app.core.config import settings
from app.core.database import get_db
from app.models import User
from app.schemas import TokenData

# ====== CONFIGURACIÓN DE HASH ======
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ====== FUNCIONES DE CONTRASEÑA CON TRUNCAMIENTO (bcrypt <= 72 bytes) ======
def get_password_hash(password: str) -> str:
    """Hashea la contraseña truncándola a 72 bytes para cumplir con bcrypt."""
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña truncándola también a 72 bytes."""
    return pwd_context.verify(plain_password[:72], hashed_password)

# ====== CONFIGURACIÓN DE TOKEN ======
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con expiración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# ====== FUNCIONES DE USUARIO ======
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Obtiene un usuario por su email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Autentica al usuario verificando email y contraseña."""
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# ====== DEPENDENCIA PARA OBTENER USUARIO ACTUAL (desde header o cookie) ======
async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual a partir del token JWT.
    Primero intenta desde el header Authorization, si no, desde la cookie 'access_token'.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return user