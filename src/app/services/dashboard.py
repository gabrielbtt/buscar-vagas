from dataclasses import dataclass

from app.core.config import PROJECT_CONTEXT_PATH, get_settings
from app.db import models  # noqa: F401
from app.db.base import Base, SessionLocal, engine
from app.db.repositories import list_recent_jobs


@dataclass(frozen=True)
class DashboardData:
    latest_status: str
    search_interval_minutes: int
    immediate_alert_min_score: float
    target_locations: list[str]
    required_keywords: list[str]
    preferred_keywords: list[str]
    blocked_keywords: list[str]
    allowed_contract_terms: list[str]
    enabled_sources: list[str]
    company_page_source_enabled: bool
    company_page_source_url: str
    preferred_execution_window: str
    recent_jobs: list[dict]


def build_dashboard_data() -> DashboardData:
    settings = get_settings(refresh=True)
    return DashboardData(
        latest_status=_read_latest_status(),
        search_interval_minutes=settings.search_interval_minutes,
        immediate_alert_min_score=settings.immediate_alert_min_score,
        target_locations=list(settings.target_locations),
        required_keywords=list(settings.required_keywords),
        preferred_keywords=list(settings.preferred_keywords),
        blocked_keywords=list(settings.blocked_keywords),
        allowed_contract_terms=list(settings.allowed_contract_terms),
        enabled_sources=_enabled_sources(settings),
        company_page_source_enabled=settings.company_page_source_enabled,
        company_page_source_url=settings.company_page_source_url,
        preferred_execution_window=settings.preferred_execution_window,
        recent_jobs=_recent_jobs(),
    )


def _read_latest_status() -> str:
    if not PROJECT_CONTEXT_PATH.exists():
        return "Aguardando primeira execucao"

    content = PROJECT_CONTEXT_PATH.read_text(encoding="utf-8")
    in_status = False
    for line in content.splitlines():
        if line == "## Current Status":
            in_status = True
            continue
        if in_status and line.startswith("## "):
            break
        if in_status and line.startswith("- "):
            return line[2:]
    return "Aguardando primeira execucao"


def _enabled_sources(settings) -> list[str]:
    sources = []
    if settings.company_page_source_enabled and settings.company_page_source_url:
        sources.append(f"company-page: {settings.company_page_source_url}")
    return sources or ["Nenhuma fonte habilitada"]


def _recent_jobs() -> list[dict]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        return [
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "score": job.score,
                "notified": job.notified,
                "source_name": job.source_name,
            }
            for job in list_recent_jobs(session)
        ]
