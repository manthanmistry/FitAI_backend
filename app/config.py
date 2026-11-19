"""
Application configuration.
Reads all secrets and settings from environment variables.
Never hardcode the OpenAI API key here.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./fitai.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    environment: str = "development"
    jwt_secret: str = "dev-change-me-fitai-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        # SQLAlchemy 2.1 treats postgresql:// as the psycopg v3 driver.
        # Render provides that URL, and this project installs psycopg2.
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://") :]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://") :]
        if url.startswith("postgresql") and "render.com" in url and "sslmode=" not in url:
            url += ("&" if "?" in url else "?") + "sslmode=require"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
