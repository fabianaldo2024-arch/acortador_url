"""
Application Configuration Module.
Módulo de Configuración de la Aplicación.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "URL Shortener API"
    SECRET_KEY: str = "super-secret-key-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql+asyncpg://postgres:secretpassword@db:5432/url_shortener_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
