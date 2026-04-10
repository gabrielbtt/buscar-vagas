from fastapi.testclient import TestClient
from sqlalchemy import insert

from app import main as main_module
from app.db import models  # noqa: F401
from app.db.base import Base, engine
from app.db.base import SessionLocal
from app.db.models import JobListing
from app.main import create_app


def test_healthcheck_returns_ok():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recent_jobs_endpoint_exists():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.execute(
            insert(JobListing).values(
                fingerprint="job-1",
                source_name="company-page",
                external_id=None,
                title="Estagio em Automacao",
                company="Empresa X",
                location="Belo Horizonte, MG",
                work_model="Presencial",
                employment_type="Estagio",
                url="https://example.com/job/1",
                description_text="vaga teste",
                score=0.91,
                notified=True,
            )
        )
        session.commit()

    client = TestClient(create_app())

    response = client.get("/admin/jobs/recent")

    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == "Estagio em Automacao"
    assert response.json()["items"][0]["notified"] is True
    assert response.json()["items"][0]["source_name"] == "company-page"


def test_create_app_builds_scheduler_from_current_settings(monkeypatch):
    captured = {}

    monkeypatch.setattr(main_module, "configure_logging", lambda: None)
    monkeypatch.setattr(
        main_module,
        "get_settings",
        lambda: type("Settings", (), {"search_interval_minutes": 45})(),
    )
    monkeypatch.setattr(
        main_module,
        "build_scheduler",
        lambda job_callable, interval_minutes: captured.update(
            {"job_callable": job_callable, "interval_minutes": interval_minutes}
        ) or object(),
    )

    app = main_module.create_app()

    assert captured["job_callable"] is main_module.run_scheduled_cycle
    assert captured["interval_minutes"] == 45
    assert app.state.scheduler is not None
