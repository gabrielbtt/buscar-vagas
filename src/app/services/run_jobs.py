import asyncio
from dataclasses import dataclass

from app.core.config import PROJECT_CONTEXT_PATH, get_settings
from app.db import models  # noqa: F401
from app.db.base import Base, SessionLocal, engine
from app.db.repositories import mark_jobs_as_notified, persist_new_matches, should_notify_for_job, upsert_fetched_jobs
from app.services.context_tracker import ensure_project_context
from app.services.matcher import match_jobs
from app.services.notifier import build_digest_email, send_digest_email
from app.core.profile import JobProfile


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
    
    # Pegar todos os perfis ativos
    active_profiles_data = [p for p in settings.profiles if p.active]
    if not active_profiles_data:
        return RunCycleResult(0, 0, 0, 0)

    jobs = asyncio.run(collector.fetch_all())
    all_matched = []
    
    for profile_data in active_profiles_data:
        profile = JobProfile(
            id=profile_data.id,
            name=profile_data.name,
            active=profile_data.active,
            required_keywords=tuple(profile_data.required_keywords),
            preferred_keywords=tuple(profile_data.preferred_keywords),
            blocked_keywords=tuple(profile_data.blocked_keywords),
            allowed_contract_terms=tuple(profile_data.allowed_contract_terms),
            target_locations=tuple(profile_data.target_locations),
            allow_remote_terms=("remoto", "remote", "home office")
        )
        matched = match_jobs(jobs, profile, settings.digest_min_score)
        all_matched.extend(matched)

    if not all_matched:
        with SessionLocal() as session:
            upsert_fetched_jobs(session, jobs)
        return RunCycleResult(len(jobs), 0, 0, 0)

    with SessionLocal() as session:
        upsert_fetched_jobs(session, jobs)
        new_items = persist_new_matches(session, all_matched)
        if not new_items:
            return RunCycleResult(
                fetched_jobs=len(jobs),
                matched_jobs=len(all_matched),
                notified_jobs=0,
                high_priority_jobs=0,
            )

        high_priority = [item for item in new_items if item.score >= settings.immediate_alert_min_score]
        normal_priority = [item for item in new_items if item.score < settings.immediate_alert_min_score]

        if normal_priority:
            send_digest_email(
                "Novas vagas encontradas",
                build_digest_email([_to_email_payload(item) for item in normal_priority]),
            )

        for item in high_priority:
            send_digest_email(
                f"Oportunidade Premium: {item.job.title}",
                build_digest_email([_to_email_payload(item)]),
            )

        mark_jobs_as_notified(session, [item.fingerprint for item in new_items])

    return RunCycleResult(
        fetched_jobs=len(jobs),
        matched_jobs=len(all_matched),
        notified_jobs=len(new_items),
        high_priority_jobs=len(high_priority),
    )


def process_job_batch(jobs):
    Base.metadata.create_all(bind=engine)
    ensure_project_context(PROJECT_CONTEXT_PATH)
    settings = get_settings()
    
    active_profiles_data = [p for p in settings.profiles if p.active]
    all_matched = []
    
    for profile_data in active_profiles_data:
        profile = JobProfile(
            id=profile_data.id,
            name=profile_data.name,
            active=profile_data.active,
            required_keywords=tuple(profile_data.required_keywords),
            preferred_keywords=tuple(profile_data.preferred_keywords),
            blocked_keywords=tuple(profile_data.blocked_keywords),
            allowed_contract_terms=tuple(profile_data.allowed_contract_terms),
            target_locations=tuple(profile_data.target_locations),
            allow_remote_terms=("remoto", "remote", "home office")
        )
        matched = match_jobs(jobs, profile, settings.digest_min_score)
        all_matched.extend(matched)

    new_items = []
    with SessionLocal() as session:
        for item in all_matched:
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
