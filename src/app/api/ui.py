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
from app.services.settings_store import DEFAULT_FILE_SETTINGS, FileSettingsStore


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
    return _build_run_now_response(result)


@router.post("/ui/settings")
async def save_settings(request: Request) -> SettingsResponse:
    form_data = await _read_form_data(request)
    store = FileSettingsStore(SETTINGS_STORE_PATH)
    payload = _build_settings_payload(form_data)
    store.save(payload)
    get_settings.cache_clear()
    settings = get_settings(refresh=True)
    sync_scheduler_interval(request.app.state.scheduler, settings=settings)
    return SettingsResponse(
        search_interval_minutes=settings.search_interval_minutes,
        immediate_alert_min_score=settings.immediate_alert_min_score,
        profiles=[
            {
                "id": profile.id,
                "name": profile.name,
                "active": profile.active,
                "required_keywords": list(profile.required_keywords),
                "preferred_keywords": list(profile.preferred_keywords),
                "blocked_keywords": list(profile.blocked_keywords),
                "allowed_contract_terms": list(profile.allowed_contract_terms),
                "target_locations": list(profile.target_locations),
                "allow_remote_terms": list(profile.allow_remote_terms),
                "use_gupy": profile.use_gupy,
                "use_vagas": profile.use_vagas,
                "custom_sources": list(profile.custom_sources),
            }
            for profile in settings.profiles
        ],
        target_locations=list(settings.target_locations),
        company_page_source_enabled=settings.company_page_source_enabled,
        company_page_source_url=settings.company_page_source_url,
        browser_page_source_enabled=settings.browser_page_source_enabled,
        browser_page_source_url=settings.browser_page_source_url,
        global_sources=list(settings.global_sources),
    )


def _split_csv(value: str) -> list[str]:
    items = []
    seen = set()
    for raw_item in value.replace("\r", "\n").replace("\n", ",").split(","):
        item = raw_item.strip()
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def _build_run_now_response(result) -> dict:
    payload = asdict(result) if hasattr(result, "__dataclass_fields__") else dict(vars(result))
    if payload.get("fetched_jobs", 0) == 0 and payload.get("notified_jobs", 0) == 0:
        message = "Busca concluida sem novas vagas aderentes."
    else:
        message = (
            f"Busca concluida: {payload.get('fetched_jobs', 0)} vagas coletadas, "
            f"{payload.get('matched_jobs', 0)} com match e {payload.get('notified_jobs', 0)} notificadas."
        )
    payload.update({"status": "ok", "message": message})
    return payload


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int((value or "").strip())
    except (TypeError, ValueError):
        return default


def _parse_float(value: str | None, default: float) -> float:
    try:
        return float((value or "").strip())
    except (TypeError, ValueError):
        return default


def _build_profile_payload(form_data: dict[str, str], pid: str) -> dict | None:
    name = form_data.get(f"profile_{pid}_name", "").strip()
    required_keywords = _split_csv(form_data.get(f"profile_{pid}_required_keywords", ""))
    preferred_keywords = _split_csv(form_data.get(f"profile_{pid}_preferred_keywords", ""))
    blocked_keywords = _split_csv(form_data.get(f"profile_{pid}_blocked_keywords", ""))
    allowed_contract_terms = _split_csv(form_data.get(f"profile_{pid}_allowed_contract_terms", ""))
    target_locations = _split_csv(form_data.get(f"profile_{pid}_target_locations", ""))
    allow_remote_terms = _split_csv(
        form_data.get(f"profile_{pid}_allow_remote_terms", "remoto, remote, home office")
    )
    custom_sources = _split_csv(form_data.get(f"profile_{pid}_custom_sources", ""))

    if not any([name, required_keywords, preferred_keywords, custom_sources]):
        return None

    return {
        "id": pid,
        "name": name or pid,
        "active": form_data.get(f"profile_{pid}_active") == "on",
        "required_keywords": required_keywords,
        "preferred_keywords": preferred_keywords,
        "blocked_keywords": blocked_keywords,
        "allowed_contract_terms": allowed_contract_terms,
        "target_locations": target_locations,
        "allow_remote_terms": allow_remote_terms,
        "use_gupy": form_data.get(f"profile_{pid}_use_gupy") == "on",
        "use_vagas": form_data.get(f"profile_{pid}_use_vagas") == "on",
        "custom_sources": custom_sources,
    }


def _build_settings_payload(form_data: dict[str, str]) -> dict:
    profile_ids = []
    for key in form_data:
        if key.startswith("profile_") and key.endswith("_name"):
            profile_ids.append(key.replace("profile_", "").replace("_name", ""))

    profiles = []
    for pid in profile_ids:
        profile_payload = _build_profile_payload(form_data, pid)
        if profile_payload is not None:
            profiles.append(profile_payload)

    return {
        "search_interval_minutes": _parse_int(
            form_data.get("search_interval_minutes"),
            DEFAULT_FILE_SETTINGS["search_interval_minutes"],
        ),
        "immediate_alert_min_score": _parse_float(
            form_data.get("immediate_alert_min_score"),
            DEFAULT_FILE_SETTINGS["immediate_alert_min_score"],
        ),
        "profiles": profiles,
        "target_locations": _split_csv(form_data.get("target_locations", "")),
        "required_keywords": _split_csv(form_data.get("required_keywords", "")),
        "preferred_keywords": _split_csv(form_data.get("preferred_keywords", "")),
        "blocked_keywords": _split_csv(form_data.get("blocked_keywords", "")),
        "allowed_contract_terms": _split_csv(form_data.get("allowed_contract_terms", "")),
        "company_page_source_enabled": form_data.get("company_page_source_enabled") == "on",
        "company_page_source_url": form_data.get("company_page_source_url", "").strip(),
        "browser_page_source_enabled": form_data.get("browser_page_source_enabled") == "on",
        "browser_page_source_url": form_data.get("browser_page_source_url", "").strip(),
        "global_sources": _split_csv(form_data.get("global_sources", "")),
        "preferred_execution_window": form_data.get("preferred_execution_window", "").strip() or "comercial",
    }


async def _read_form_data(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items()}
