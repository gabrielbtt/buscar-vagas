from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.core.config import SETTINGS_STORE_PATH, get_settings
from app.main import create_app
from app.schemas.job import NormalizedJob
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

    # Enviamos dados no novo formato (incluindo pelo menos um perfil para ser processado)
    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": 30,
            "immediate_alert_min_score": 0.92,
            "profile_test_name": "Perfil Teste",
            "profile_test_active": "on",
            "profile_test_required_keywords": "eng eletrica, clp",
        },
        follow_redirects=False # Queremos testar o 303 explicitamente
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    
    # Verificar se salvou no disco
    settings = get_settings(refresh=True)
    assert settings.search_interval_minutes == 30
    assert settings.immediate_alert_min_score == 0.92
    assert any(p.name == "Perfil Teste" for p in settings.profiles)


def test_dashboard_shows_recent_fetched_jobs_after_manual_run(monkeypatch):
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "profiles": [
                {
                    "id": "test",
                    "name": "Perfil Teste",
                    "active": True,
                    "required_keywords": ["engenharia eletrica"],
                    "preferred_keywords": ["clp"],
                    "blocked_keywords": [],
                    "allowed_contract_terms": ["estagio"],
                    "target_locations": ["belo horizonte"],
                    "allow_remote_terms": ["remoto", "remote", "home office"],
                    "use_gupy": False,
                    "use_vagas": False,
                    "custom_sources": [],
                }
            ],
        }
    )
    get_settings.cache_clear()

    class FakeCollector:
        async def fetch_all(self):
            return [
                NormalizedJob(
                    source_name="Manual",
                    title="Estagio Administrativo",
                    company="Empresa X",
                    location="Belo Horizonte, MG",
                    work_model="Presencial",
                    employment_type="Estagio",
                    url="https://example.com/jobs/1",
                    description_text="rotinas administrativas e planilhas",
                )
            ]

    monkeypatch.setattr("app.api.ui.build_runtime_collector", lambda settings: FakeCollector())
    client = TestClient(create_app())

    run_response = client.post("/ui/run-now")
    dashboard_response = client.get("/")

    assert run_response.status_code == 200
    assert run_response.json()["fetched_jobs"] == 1
    assert "Estagio Administrativo" in dashboard_response.text


def test_dashboard_page_exposes_global_source_url_fields():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "company_page_source_enabled": True,
            "company_page_source_url": "https://example.com/company/jobs",
            "browser_page_source_enabled": True,
            "browser_page_source_url": "https://example.com/browser/jobs",
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert 'name="company_page_source_url"' in response.text
    assert 'name="browser_page_source_url"' in response.text
    assert "https://example.com/company/jobs" in response.text
    assert "https://example.com/browser/jobs" in response.text


def test_dashboard_page_exposes_global_sources_textarea():
    FileSettingsStore(SETTINGS_STORE_PATH).save(
        {
            **DEFAULT_FILE_SETTINGS,
            "global_sources": [
                "https://www.infojobs.com.br/",
                "https://www.catho.com.br/vagas/",
            ],
        }
    )
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert 'name="global_sources"' in response.text
    assert "https://www.infojobs.com.br/" in response.text
    assert "https://www.catho.com.br/vagas/" in response.text


def test_ui_settings_form_persists_global_source_urls():
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": "30",
            "immediate_alert_min_score": "0.92",
            "company_page_source_enabled": "on",
            "company_page_source_url": "https://example.com/company/jobs",
            "browser_page_source_enabled": "on",
            "browser_page_source_url": "https://example.com/browser/jobs",
            "profile_test_name": "Perfil Teste",
            "profile_test_active": "on",
            "profile_test_required_keywords": "eng eletrica, clp",
        },
        follow_redirects=False,
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 303
    assert settings.company_page_source_url == "https://example.com/company/jobs"
    assert settings.browser_page_source_url == "https://example.com/browser/jobs"


def test_ui_settings_form_persists_global_sources():
    FileSettingsStore(SETTINGS_STORE_PATH).save(DEFAULT_FILE_SETTINGS)
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/ui/settings",
        data={
            "search_interval_minutes": "30",
            "immediate_alert_min_score": "0.92",
            "global_sources": "https://www.infojobs.com.br/, https://www.catho.com.br/vagas/",
            "profile_test_name": "Perfil Teste",
            "profile_test_active": "on",
            "profile_test_required_keywords": "eng eletrica, clp",
        },
        follow_redirects=False,
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 303
    assert settings.global_sources == (
        "https://www.infojobs.com.br/",
        "https://www.catho.com.br/vagas/",
    )


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
        follow_redirects=False,
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 303
    assert settings.search_interval_minutes == 180
    assert settings.immediate_alert_min_score == 0.9
    assert settings.global_sources == (
        "https://a.com/jobs",
        "https://b.com/jobs",
    )
    profile = next(p for p in settings.profiles if p.id == "test")
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
        follow_redirects=False,
    )

    settings = get_settings(refresh=True)

    assert response.status_code == 303
    assert all(profile.id != "empty" for profile in settings.profiles)
