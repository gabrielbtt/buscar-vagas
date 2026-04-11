from fastapi.testclient import TestClient

from app.core.config import SETTINGS_STORE_PATH, get_settings
from app.main import create_app
from app.services.settings_store import DEFAULT_FILE_SETTINGS, FileSettingsStore


def test_dashboard_page_returns_html():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            "company_page_source_enabled": True,
            "company_page_source_url": "https://example.com/company/jobs",
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Busca de Vagas" in response.text
    assert "Buscar agora" in response.text
    assert 'name="search_interval_minutes"' in response.text
    assert "Vagas Recentes" in response.text
    assert "Perfis de Busca" in response.text


def test_manual_run_endpoint_returns_summary():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "company_page_source_enabled": False,
            "company_page_source_url": "",
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post("/ui/run-now")

    assert response.status_code == 200
    assert "fetched_jobs" in response.json()


def test_ui_settings_form_updates_scheduler_and_alert_threshold():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "company_page_source_enabled": False,
            "company_page_source_url": "",
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": 30,
            "immediate_alert_min_score": 0.92,
            "target_locations": "belo horizonte, contagem, remoto",
        },
    )

    assert response.status_code == 200
    assert response.json()["search_interval_minutes"] == 30
