from dataclasses import asdict
from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import ROOT_DIR, SETTINGS_STORE_PATH, get_settings
from app.schemas.ui import SettingsResponse
from app.services.collector import MultiSourceCollector
from app.services.dashboard import build_dashboard_data
from app.services.run_jobs import run_collection_cycle
from app.services.scheduler import build_runtime_collector, sync_scheduler_interval
from app.services.settings_store import FileSettingsStore


templates = Jinja2Templates(directory=str(ROOT_DIR / "src" / "app" / "templates"))
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"data": build_dashboard_data()},
    )


@router.post("/ui/run-now")
def run_now(request: Request) -> dict:
    settings = get_settings(refresh=True)
    collector = build_runtime_collector(settings)
    result = run_collection_cycle(collector)
    sync_scheduler_interval(request.app.state.scheduler, settings=settings)
    return asdict(result)


@router.post("/ui/settings")
async def save_settings(request: Request) -> SettingsResponse:
    form_data = await _read_form_data(request)
    store = FileSettingsStore(SETTINGS_STORE_PATH)
    payload = {
        "search_interval_minutes": int(form_data["search_interval_minutes"]),
        "immediate_alert_min_score": float(form_data["immediate_alert_min_score"]),
        "target_locations": _split_csv(form_data["target_locations"]),
        "required_keywords": _split_csv(form_data.get("required_keywords", "")),
        "preferred_keywords": _split_csv(form_data.get("preferred_keywords", "")),
        "blocked_keywords": _split_csv(form_data.get("blocked_keywords", "")),
        "allowed_contract_terms": _split_csv(form_data.get("allowed_contract_terms", "")),
        "company_page_source_enabled": form_data.get("company_page_source_enabled") == "on",
        "company_page_source_url": form_data.get("company_page_source_url", "").strip(),
        "preferred_execution_window": form_data.get("preferred_execution_window", "").strip() or "comercial",
    }
    store.save(payload)
    get_settings.cache_clear()
    settings = get_settings(refresh=True)
    sync_scheduler_interval(request.app.state.scheduler, settings=settings)
    return SettingsResponse(
        search_interval_minutes=settings.search_interval_minutes,
        immediate_alert_min_score=settings.immediate_alert_min_score,
        target_locations=list(settings.target_locations),
        company_page_source_enabled=settings.company_page_source_enabled,
        company_page_source_url=settings.company_page_source_url,
    )


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


async def _read_form_data(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items()}
