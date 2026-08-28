# app/core/config.py
class Settings:
    DATABASE_URL: str = "sqlite+aiosqlite:///./url_shortener.db"
    SECRET_KEY: str = "tu-clave-secreta-cambiar"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()