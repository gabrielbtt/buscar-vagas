import asyncio
from dataclasses import dataclass
from dataclasses import replace

from app.core.config import PROJECT_CONTEXT_PATH, get_settings
from app.core.profile import build_default_profile
from app.db import models  # noqa: F401
from app.db.base import Base, SessionLocal, engine
from app.db.repositories import mark_jobs_as_notified, persist_new_matches, should_notify_for_job
from app.services.context_tracker import ensure_project_context
from app.services.matcher import match_jobs
from app.services.notifier import build_digest_email, send_digest_email


@dataclass(frozen=True)
class RunCycleResult:
    fetched_jobs: int
    matched_jobs: int
    notified_jobs: int
    high_priority_jobs: int


def run_collection_cycle(collector) -> RunCycleResult:
    Base.metadata.create_all(bind=engine)
    ensure_project_context(PROJECT_CONTEXT_PATH)
    settings = get_settings()
    profile = replace(build_default_profile(), target_locations=tuple(settings.target_locations))
    jobs = asyncio.run(collector.fetch_all())
    matched = match_jobs(jobs, profile, settings.digest_min_score)
    with SessionLocal() as session:
        new_items = persist_new_matches(session, matched)
        if not new_items:
            return RunCycleResult(
                fetched_jobs=len(jobs),
                matched_jobs=len(matched),
                notified_jobs=0,
                high_priority_jobs=0,
            )

        high_priority = [item for item in new_items if item.score >= settings.immediate_alert_min_score]
        normal_priority = [item for item in new_items if item.score < settings.immediate_alert_min_score]

        if normal_priority:
            send_digest_email(
                "Vagas encontradas",
                build_digest_email([_to_email_payload(item) for item in normal_priority]),
            )

        for item in high_priority:
            send_digest_email(
                f"Oportunidade muito boa: {item.job.title}",
                build_digest_email([_to_email_payload(item)]),
            )

        mark_jobs_as_notified(session, [item.fingerprint for item in new_items])

    return RunCycleResult(
        fetched_jobs=len(jobs),
        matched_jobs=len(matched),
        notified_jobs=len(new_items),
        high_priority_jobs=len(high_priority),
    )


def process_job_batch(jobs):
    Base.metadata.create_all(bind=engine)
    ensure_project_context(PROJECT_CONTEXT_PATH)
    settings = get_settings()
    profile = replace(build_default_profile(), target_locations=tuple(settings.target_locations))
    matched = match_jobs(jobs, profile, settings.digest_min_score)
    new_items = []
    with SessionLocal() as session:
        for item in matched:
            if should_notify_for_job(session, item):
                new_items.append(item)
        mark_jobs_as_notified(session, [item.fingerprint for item in new_items])
    return new_items


def _to_email_payload(item) -> dict:
    return {
        "title": item.job.title,
        "company": item.job.company,
        "location": item.job.location,
        "score": item.score,
        "url": str(item.job.url),
    }
