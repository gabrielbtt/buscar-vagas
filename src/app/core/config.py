from functools import lru_cache
from pathlib import Path

from pydantic import EmailStr, TypeAdapter, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.services.settings_store import DEFAULT_FILE_SETTINGS, FileSettingsStore


ROOT_DIR = Path(__file__).resolve().parents[3]
KILO_DIR = ROOT_DIR / ".kilo"
PROJECT_CONTEXT_PATH = KILO_DIR / "project-context.md"
SETTINGS_STORE_PATH = KILO_DIR / "ui-settings.json"


class Settings(BaseSettings):
    app_name: str = "busca-vagas"
    environment: str = "development"
    database_url: str = "sqlite:///./jobs.db"
    search_interval_minutes: int = 180
    immediate_alert_min_score: float = DEFAULT_FILE_SETTINGS["immediate_alert_min_score"]
    digest_min_score: float = 0.6
    target_locations: tuple[str, ...] = tuple(DEFAULT_FILE_SETTINGS["target_locations"])
    required_keywords: tuple[str, ...] = tuple(DEFAULT_FILE_SETTINGS["required_keywords"])
    preferred_keywords: tuple[str, ...] = tuple(DEFAULT_FILE_SETTINGS["preferred_keywords"])
    blocked_keywords: tuple[str, ...] = tuple(DEFAULT_FILE_SETTINGS["blocked_keywords"])
    allowed_contract_terms: tuple[str, ...] = tuple(DEFAULT_FILE_SETTINGS["allowed_contract_terms"])
    company_page_source_enabled: bool = False
    company_page_source_url: str = ""
    browser_page_source_enabled: bool = False
    browser_page_source_url: str = ""
    preferred_execution_window: str = DEFAULT_FILE_SETTINGS["preferred_execution_window"]
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
def _get_cached_settings() -> Settings:
    store = FileSettingsStore(SETTINGS_STORE_PATH)
    stored_settings = store.load()
    settings = Settings()
    overrides = {}
    for key, value in stored_settings.items():
        if key not in Settings.model_fields:
            continue

        field = Settings.model_fields[key]
        try:
            overrides[key] = TypeAdapter(field.annotation).validate_python(value)
        except ValidationError:
            continue
    return settings.model_copy(update=overrides)


def get_settings(*, refresh: bool = False) -> Settings:
    if refresh:
        return _get_cached_settings.__wrapped__()
    return _get_cached_settings()


get_settings.cache_clear = _get_cached_settings.cache_clear
