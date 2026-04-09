from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models import JobListing
from app.services.matcher import MatchedJob


def should_notify_for_job(session, matched_job: MatchedJob) -> bool:
    existing = session.scalar(select(JobListing).where(JobListing.fingerprint == matched_job.fingerprint))
    if existing:
        return False
    now = datetime.now(timezone.utc)
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
