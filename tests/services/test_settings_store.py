import json
from pathlib import Path

import pytest

from app.core import config as config_module
from app.services.settings_store import DEFAULT_FILE_SETTINGS, FileSettingsStore


def test_file_settings_store_returns_defaults_when_file_missing(tmp_path):
    settings_path = tmp_path / "settings.json"

    store = FileSettingsStore(settings_path)

    assert store.load() == DEFAULT_FILE_SETTINGS


def test_file_settings_store_persists_and_loads_settings(tmp_path):
    settings_path = tmp_path / "settings.json"
    store = FileSettingsStore(settings_path)

    store.save(
        {
            "search_interval_minutes": 45,
            "immediate_alert_min_score": 0.9,
            "target_locations": ["belo horizonte", "remote"],
        }
    )

    assert settings_path.exists()
    assert store.load() == {
        **DEFAULT_FILE_SETTINGS,
        "search_interval_minutes": 45,
        "immediate_alert_min_score": 0.9,
        "target_locations": ["belo horizonte", "remote"],
    }


def test_file_settings_store_save_preserves_existing_unknown_keys(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": 60,
                "custom_setting": {"enabled": True},
            }
        ),
        encoding="utf-8",
    )
    store = FileSettingsStore(settings_path)

    store.save({"target_locations": ["belo horizonte", "remote"]})

    assert json.loads(settings_path.read_text(encoding="utf-8")) == {
        **DEFAULT_FILE_SETTINGS,
        "search_interval_minutes": 60,
        "immediate_alert_min_score": 0.9,
        "target_locations": ["belo horizonte", "remote"],
        "custom_setting": {"enabled": True},
    }


def test_file_settings_store_returns_defaults_when_json_is_invalid(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{invalid json", encoding="utf-8")

    store = FileSettingsStore(settings_path)

    assert store.load() == DEFAULT_FILE_SETTINGS


def test_get_settings_ignores_unknown_file_settings_keys(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": 45,
                "unknown_setting": "keep-me",
            }
        ),
        encoding="utf-8",
    )

    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.search_interval_minutes == 45
    assert json.loads(settings_path.read_text(encoding="utf-8"))["unknown_setting"] == "keep-me"

    config_module.get_settings.cache_clear()


def test_get_settings_ignores_invalid_file_setting_values(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": "oops",
                "target_locations": ["belo horizonte", "remote"],
            }
        ),
        encoding="utf-8",
    )

    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.search_interval_minutes == 180
    assert settings.target_locations == ("belo horizonte", "remote")

    config_module.get_settings.cache_clear()


def test_get_settings_does_not_overwrite_invalid_settings_file(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    original_content = "{invalid json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(original_content, encoding="utf-8")

    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.search_interval_minutes == 180
    assert settings_path.read_text(encoding="utf-8") == original_content

    config_module.get_settings.cache_clear()


def test_get_settings_does_not_create_project_context_file(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    context_path = kilo_dir / "project-context.md"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps({"search_interval_minutes": 45}), encoding="utf-8")

    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", context_path)
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.search_interval_minutes == 45
    assert not context_path.exists()

    config_module.get_settings.cache_clear()


def test_get_settings_prefers_persisted_interval_over_env(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps({"search_interval_minutes": 45}), encoding="utf-8")

    monkeypatch.setenv("SEARCH_INTERVAL_MINUTES", "30")
    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.search_interval_minutes == 45

    config_module.get_settings.cache_clear()


def test_get_settings_prefers_persisted_source_settings_over_env(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "company_page_source_enabled": True,
                "company_page_source_url": "https://example.com/company/jobs",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("COMPANY_PAGE_SOURCE_ENABLED", "false")
    monkeypatch.setenv("COMPANY_PAGE_SOURCE_URL", "https://env.example/jobs")
    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    settings = config_module.get_settings()

    assert settings.company_page_source_enabled is True
    assert settings.company_page_source_url == "https://example.com/company/jobs"

    config_module.get_settings.cache_clear()


def test_get_settings_refresh_reads_updated_persisted_values(tmp_path, monkeypatch):
    kilo_dir = tmp_path / ".kilo"
    settings_path = kilo_dir / "ui-settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps({"search_interval_minutes": 45}), encoding="utf-8")

    config_module.get_settings.cache_clear()
    monkeypatch.setattr(config_module, "KILO_DIR", kilo_dir)
    monkeypatch.setattr(config_module, "PROJECT_CONTEXT_PATH", kilo_dir / "project-context.md")
    monkeypatch.setattr(config_module, "SETTINGS_STORE_PATH", settings_path)

    first = config_module.get_settings()
    settings_path.write_text(json.dumps({"search_interval_minutes": 60}), encoding="utf-8")
    refreshed = config_module.get_settings(refresh=True)

    assert first.search_interval_minutes == 45
    assert refreshed.search_interval_minutes == 60

    config_module.get_settings.cache_clear()


def test_file_settings_store_save_keeps_existing_file_when_write_fails(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    original_content = json.dumps({"search_interval_minutes": 60}, indent=2) + "\n"
    settings_path.write_text(original_content, encoding="utf-8")
    store = FileSettingsStore(settings_path)

    original_write_text = Path.write_text

    def failing_write_text(self, data, *args, **kwargs):
        original_write_text(self, "{broken", *args, **kwargs)
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", failing_write_text)

    with pytest.raises(OSError):
        store.save({"search_interval_minutes": 45})

    assert settings_path.read_text(encoding="utf-8") == original_content
