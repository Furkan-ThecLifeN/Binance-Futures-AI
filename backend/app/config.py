from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Binance Futures AI Market Intelligence"
    app_version: str = "0.1.0"
    environment: str = "development"

    api_prefix: str = "/api"

    frontend_origin: str = "http://localhost:5173"

    database_url: str = (
        "postgresql+asyncpg://"
        "futures_ai:change_me_local_password"
        "@localhost:5432/futures_ai"
    )

    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()