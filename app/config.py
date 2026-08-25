from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_aqui"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Base de datos
    DATABASE_URL: str = "sqlite+aiosqlite:///./url_shortener.db"
    
    # Entorno
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
