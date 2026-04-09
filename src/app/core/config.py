from functools import lru_cache

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "busca-vagas"
    environment: str = "development"
    database_url: str = "sqlite:///./jobs.db"
    search_interval_minutes: int = 180
    digest_min_score: float = 0.6
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: EmailStr = "alerts@example.com"
    email_to: EmailStr = "alerts@example.com"
    playwright_mcp_url: str = "http://localhost:8931"
    playwright_headless: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
