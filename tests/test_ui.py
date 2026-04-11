from fastapi.testclient import TestClient
from types import SimpleNamespace

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


def test_ui_settings_form_normalizes_multiline_lists_and_missing_checkboxes():
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": "",
            "immediate_alert_min_score": "not-a-number",
            "global_sources": "https://a.com/jobs\nhttps://b.com/jobs\nhttps://a.com/jobs ",
            "profile_test_name": "Perfil Teste",
            "profile_test_required_keywords": "engenharia eletrica\nclp",
            "profile_test_custom_sources": "https://empresa.com/jobs, https://empresa.com/jobs ",
        },
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 200
    assert settings.search_interval_minutes == 180
    assert settings.immediate_alert_min_score == 0.9
    assert settings.global_sources == (
        "https://a.com/jobs",
        "https://b.com/jobs",
    )
    profile = next(p for p in settings.profiles if p.name == "Perfil Teste")
    assert profile.active is False
    assert profile.use_gupy is False
    assert profile.use_vagas is False
    assert profile.required_keywords == ("engenharia eletrica", "clp")
    assert profile.custom_sources == ("https://empresa.com/jobs",)


def test_ui_settings_form_ignores_blank_profiles_without_name_and_keywords():
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": "30",
            "immediate_alert_min_score": "0.92",
            "profile_empty_name": "   ",
            "profile_empty_required_keywords": "   ",
        },
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 200
    assert all(profile.name.strip() for profile in settings.profiles)


def test_dashboard_page_groups_operational_sections():
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Resumo Operacional" in response.text
    assert "Fontes Globais" in response.text
    assert "Fontes Legadas" in response.text
    assert "Perfis de Busca" in response.text
    assert "Salvar Configuracoes" in response.text


def test_manual_run_endpoint_returns_operational_summary(monkeypatch):
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()

    class FakeCollector:
        async def fetch_all(self):
            return []

    monkeypatch.setattr("app.api.ui.build_runtime_collector", lambda settings: FakeCollector())
    monkeypatch.setattr(
        "app.api.ui.run_collection_cycle",
        lambda collector: SimpleNamespace(
            fetched_jobs=0,
            matched_jobs=0,
            notified_jobs=0,
            high_priority_jobs=0,
        ),
    )
    client = TestClient(create_app())

    response = client.post("/ui/run-now")

    assert response.status_code == 200
    assert response.json() == {
        "fetched_jobs": 0,
        "matched_jobs": 0,
        "notified_jobs": 0,
        "high_priority_jobs": 0,
        "status": "ok",
        "message": "Busca concluida sem novas vagas aderentes.",
    }


def test_dashboard_page_renders_normalized_global_sources_once():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "global_sources": [
                "https://www.infojobs.com.br/",
                "https://www.infojobs.com.br/ ",
                "https://www.catho.com.br/vagas/",
            ],
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.text.count("https://www.infojobs.com.br/") == 1
