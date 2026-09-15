"""
Security and Password Hashing Module.
Módulo de Seguridad y Hashing de Contraseñas.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash / Verificar contraseña."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash / Generar hash bcrypt."""
    return pwd_context.hash(password)
