from app.core.config import get_settings
from app.core.profile import build_default_profile
from app.db import models  # noqa: F401
from app.db.base import Base, SessionLocal, engine
from app.db.repositories import should_notify_for_job
from app.services.matcher import match_jobs


def process_job_batch(jobs):
    Base.metadata.create_all(bind=engine)
    profile = build_default_profile()
    settings = get_settings()
    matched = match_jobs(jobs, profile, settings.digest_min_score)
    new_items = []
    with SessionLocal() as session:
        for item in matched:
            if should_notify_for_job(session, item):
                new_items.append(item)
    return new_items
