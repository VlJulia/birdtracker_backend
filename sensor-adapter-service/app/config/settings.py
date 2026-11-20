import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class _Settings(BaseSettings):

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_TCP_PORT: int = 9999
    ENABLE_TCP_SERVER: bool = False
    APP_UDP_PORT: int = 9998
    ENABLE_UDP_SERVER: bool = False

    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @model_validator(mode="after")
    def _build_database_url(self):
        if not self.DATABASE_URL:
            user = os.getenv("POSTGRES_USER", "")
            password = os.getenv("POSTGRES_PASSWORD", "")
            host = os.getenv("POSTGRES_HOST", "")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "")
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
            )
        return self


settings = _Settings()
