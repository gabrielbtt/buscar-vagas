from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import JobListing
from app.schemas.job import NormalizedJob
from app.services import run_jobs


class FakeCollector:
    def __init__(self, jobs):
        self._jobs = jobs

    async def fetch_all(self):
        return self._jobs


def test_run_collection_cycle_returns_sent_digest_metadata(monkeypatch):
    sent_messages = []
    session_factory = _configure_test_runtime(monkeypatch, immediate_alert_min_score=0.9)
    collector = FakeCollector([_build_job(title="Estagio em Engenharia Eletrica", description="engenharia eletrica clp ihm")])

    monkeypatch.setattr(
        run_jobs,
        "send_digest_email",
        lambda subject, html: sent_messages.append((subject, html)),
    )

    result = run_jobs.run_collection_cycle(collector)

    assert result.fetched_jobs == 1
    assert result.matched_jobs == 1
    assert result.notified_jobs == 1
    assert result.high_priority_jobs == 0
    assert sent_messages[0][0] == "Vagas encontradas"

    with session_factory() as session:
        saved = session.scalar(select(JobListing))
        assert saved is not None
        assert saved.notified is True


def test_run_collection_cycle_sends_immediate_alert_for_exceptional_job(monkeypatch):
    sent_messages = []
    _configure_test_runtime(monkeypatch, immediate_alert_min_score=0.9)
    collector = FakeCollector(
        [
            _build_job(
                title="Estagio em Engenharia Eletrica e Automacao Industrial",
                description="engenharia eletrica clp ihm automacao industrial",
            )
        ]
    )

    monkeypatch.setattr(
        run_jobs,
        "send_digest_email",
        lambda subject, html: sent_messages.append((subject, html)),
    )

    result = run_jobs.run_collection_cycle(collector)

    assert result.fetched_jobs == 1
    assert result.matched_jobs == 1
    assert result.notified_jobs == 1
    assert result.high_priority_jobs == 1
    assert sent_messages[0][0].startswith("Oportunidade muito boa:")


def test_process_job_batch_returns_only_new_matches(monkeypatch):
    _configure_test_runtime(monkeypatch, immediate_alert_min_score=0.9)
    jobs = [
        _build_job(
            title="Estagio em Automacao Industrial",
            description="engenharia eletrica clp ihm",
        )
    ]

    first = run_jobs.process_job_batch(jobs)
    second = run_jobs.process_job_batch(jobs)

    assert len(first) == 1
    assert second == []


def test_run_collection_cycle_retries_persisted_unnotified_job(monkeypatch):
    session_factory = _configure_test_runtime(monkeypatch, immediate_alert_min_score=0.9)
    collector = FakeCollector([_build_job(title="Estagio em Engenharia Eletrica", description="engenharia eletrica clp ihm")])
    delivery_attempts = []

    def fail_once(subject, html):
        delivery_attempts.append(subject)
        raise RuntimeError("smtp unavailable")

    monkeypatch.setattr(run_jobs, "send_digest_email", fail_once)

    with pytest.raises(RuntimeError):
        run_jobs.run_collection_cycle(collector)

    with session_factory() as session:
        saved = session.scalar(select(JobListing))
        assert saved is not None
        assert saved.notified is False

    monkeypatch.setattr(
        run_jobs,
        "send_digest_email",
        lambda subject, html: delivery_attempts.append(subject),
    )

    result = run_jobs.run_collection_cycle(collector)

    assert result.notified_jobs == 1
    assert delivery_attempts == ["Vagas encontradas", "Vagas encontradas"]

    with session_factory() as session:
        saved = session.scalar(select(JobListing))
        assert saved is not None
        assert saved.notified is True


def _configure_test_runtime(monkeypatch, immediate_alert_min_score: float):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(run_jobs, "engine", engine)
    monkeypatch.setattr(run_jobs, "SessionLocal", session_factory)
    monkeypatch.setattr(run_jobs, "PROJECT_CONTEXT_PATH", engine.url.database or "project-context.md")
    monkeypatch.setattr(run_jobs, "ensure_project_context", lambda path: path)
    monkeypatch.setattr(
        run_jobs,
        "get_settings",
        lambda: SimpleNamespace(
            digest_min_score=0.6,
            immediate_alert_min_score=immediate_alert_min_score,
            target_locations=("belo horizonte", "contagem", "betim", "nova lima"),
        ),
    )
    return session_factory


def _build_job(*, title: str, description: str) -> NormalizedJob:
    return NormalizedJob(
        source_name="company-page",
        title=title,
        company="Empresa X",
        location="Belo Horizonte, MG",
        work_model="Presencial",
        employment_type="Estagio",
        url="https://example.com/job/1",
        description_text=description,
    )
