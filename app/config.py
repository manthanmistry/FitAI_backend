"""
Application configuration.
Reads all secrets and settings from environment variables.
Never hardcode the OpenAI API key here.
"""
import os
import re

from pydantic_settings import BaseSettings
from functools import lru_cache

# dpg-abc-a.singapore-postgres.render.com -> dpg-abc-a
_RENDER_POSTGRES_HOST = re.compile(
    r"(dpg-[a-z0-9]+-a)\.[a-z0-9-]+-postgres\.render\.com",
    re.IGNORECASE,
)


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
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]

        # The public Render hostname drops SSL from inside Render.
        # Use the private hostname when this process is running there.
        if os.environ.get("RENDER", "").lower() == "true":
            url = _RENDER_POSTGRES_HOST.sub(r"\1", url)
            base, sep, query = url.partition("?")
            if sep:
                pairs = [
                    part
                    for part in query.split("&")
                    if part and not part.startswith("sslmode=")
                ]
                url = base + (("?" + "&".join(pairs)) if pairs else "")

        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://") :]
        elif url.startswith("postgresql+psycopg2://"):
            url = "postgresql+psycopg://" + url[len("postgresql+psycopg2://") :]

        if url.startswith("postgresql") and "render.com" in url and "sslmode=" not in url:
            url += ("&" if "?" in url else "?") + "sslmode=require"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
