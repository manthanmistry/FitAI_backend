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
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    environment: str = "development"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
