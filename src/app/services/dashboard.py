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
    profiles: list[dict]
    enabled_sources: list[str]
    company_page_source_enabled: bool
    company_page_source_url: str
    browser_page_source_enabled: bool
    browser_page_source_url: str
    global_sources: list[str]
    preferred_execution_window: str
    recent_jobs: list[dict]


def build_dashboard_data() -> DashboardData:
    settings = get_settings(refresh=True)
    return DashboardData(
        latest_status=_read_latest_status(),
        search_interval_minutes=settings.search_interval_minutes,
        immediate_alert_min_score=settings.immediate_alert_min_score,
        profiles=[_to_profile_dict(p) for p in settings.profiles],
        enabled_sources=_enabled_sources(settings),
        company_page_source_enabled=settings.company_page_source_enabled,
        company_page_source_url=settings.company_page_source_url,
        browser_page_source_enabled=settings.browser_page_source_enabled,
        browser_page_source_url=settings.browser_page_source_url,
        global_sources=list(getattr(settings, "global_sources", ())),
        preferred_execution_window=settings.preferred_execution_window,
        recent_jobs=_recent_jobs(),
    )


def _to_profile_dict(p) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "active": p.active,
        "target_locations": list(p.target_locations),
        "required_keywords": list(p.required_keywords),
        "preferred_keywords": list(p.preferred_keywords),
        "blocked_keywords": list(p.blocked_keywords),
        "allowed_contract_terms": list(p.allowed_contract_terms),
        "allow_remote_terms": list(p.allow_remote_terms),
        "use_gupy": getattr(p, "use_gupy", True),
        "use_vagas": getattr(p, "use_vagas", True),
        "custom_sources": list(getattr(p, "custom_sources", [])),
    }


def _read_latest_status() -> str:
    if not PROJECT_CONTEXT_PATH.exists():
        return "Aguardando primeira execucao"

    content = PROJECT_CONTEXT_PATH.read_text(encoding="utf-8")
    for line in content.splitlines():
        if "Estado Atual" in line:
            return line.replace("## Estado Atual", "").strip(" ()-")
        if line.startswith("- "):
            return line[2:]
    return "Aguardando primeira execucao"


def _enabled_sources(settings) -> list[str]:
    sources = []
    if settings.company_page_source_enabled and settings.company_page_source_url:
        sources.append(f"Empresa: {settings.company_page_source_url}")

    for url in getattr(settings, "global_sources", ()):
        sources.append(f"Global: {url}")
    
    # Adicionar fontes baseadas em perfis ativos
    for p in settings.profiles:
        if p.active:
            if getattr(p, "use_gupy", True):
                sources.append(f"Gupy ({p.name})")
            if getattr(p, "use_vagas", True):
                sources.append(f"Vagas.com ({p.name})")
            for cs in getattr(p, "custom_sources", []):
                sources.append(f"Manual: {cs}")
            
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
                "url": job.url,
            }
            for job in list_recent_jobs(session)
        ]
