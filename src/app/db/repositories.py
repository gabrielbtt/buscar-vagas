from datetime import datetime, timezone

from sqlalchemy import select

from app.core.dedupe import build_job_fingerprint
from app.db.models import JobListing
from app.schemas.job import NormalizedJob
from app.services.matcher import MatchedJob


def upsert_fetched_jobs(session, jobs: list[NormalizedJob]) -> None:
    now = datetime.now(timezone.utc)
    for job in jobs:
        fingerprint = build_job_fingerprint(job.company, job.title, str(job.url))
        existing = session.scalar(select(JobListing).where(JobListing.fingerprint == fingerprint))
        if existing:
            existing.source_name = job.source_name
            existing.external_id = job.external_id
            existing.title = job.title
            existing.company = job.company
            existing.location = job.location
            existing.work_model = job.work_model
            existing.employment_type = job.employment_type
            existing.url = str(job.url)
            existing.description_text = job.description_text
            existing.last_seen_at = now
            continue

        session.add(
            JobListing(
                fingerprint=fingerprint,
                source_name=job.source_name,
                external_id=job.external_id,
                title=job.title,
                company=job.company,
                location=job.location,
                work_model=job.work_model,
                employment_type=job.employment_type,
                url=str(job.url),
                description_text=job.description_text,
                score=0.0,
                first_seen_at=now,
                last_seen_at=now,
                notified=False,
            )
        )

    session.commit()


def should_notify_for_job(session, matched_job: MatchedJob) -> bool:
    existing = session.scalar(select(JobListing).where(JobListing.fingerprint == matched_job.fingerprint))
    now = datetime.now(timezone.utc)
    if existing:
        existing.last_seen_at = now
        existing.score = matched_job.score
        existing.source_name = matched_job.job.source_name
        existing.external_id = matched_job.job.external_id
        existing.title = matched_job.job.title
        existing.company = matched_job.job.company
        existing.location = matched_job.job.location
        existing.work_model = matched_job.job.work_model
        existing.employment_type = matched_job.job.employment_type
        existing.url = str(matched_job.job.url)
        existing.description_text = matched_job.job.description_text
        session.commit()
        if not existing.notified:
            return True
        return False

    session.add(
        JobListing(
            fingerprint=matched_job.fingerprint,
            source_name=matched_job.job.source_name,
            external_id=matched_job.job.external_id,
            title=matched_job.job.title,
            company=matched_job.job.company,
            location=matched_job.job.location,
            work_model=matched_job.job.work_model,
            employment_type=matched_job.job.employment_type,
            url=str(matched_job.job.url),
            description_text=matched_job.job.description_text,
            score=matched_job.score,
            first_seen_at=now,
            last_seen_at=now,
            notified=False,
        )
    )
    session.commit()
    return True


def persist_new_matches(session, matched_jobs: list[MatchedJob]) -> list[MatchedJob]:
    new_items: list[MatchedJob] = []
    for item in matched_jobs:
        if should_notify_for_job(session, item):
            new_items.append(item)
    return new_items


def mark_jobs_as_notified(session, fingerprints: list[str]) -> None:
    if not fingerprints:
        return

    records = session.scalars(select(JobListing).where(JobListing.fingerprint.in_(fingerprints))).all()
    for record in records:
        record.notified = True
    session.commit()


def list_recent_jobs(session, limit: int = 10) -> list[JobListing]:
    statement = select(JobListing).order_by(JobListing.last_seen_at.desc()).limit(limit)
    return list(session.scalars(statement).all())
