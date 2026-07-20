from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "StageFlow API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Base de données
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # Sécurité JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


@lru_cache()
def get_settings() -> Settings:
    """Cache la configuration pour éviter les relectures du .env."""
    return Settings()


settings = get_settings()