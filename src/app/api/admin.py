from fastapi import APIRouter

from app.db import models  # noqa: F401
from app.db.base import Base, SessionLocal, engine
from app.db.repositories import list_recent_jobs
from app.schemas.run import RecentJobItem, RecentJobsResponse

router = APIRouter(prefix="/admin")


@router.get("/jobs/recent", response_model=RecentJobsResponse)
def recent_jobs() -> RecentJobsResponse:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        items = [
            RecentJobItem(
                company=job.company,
                title=job.title,
                location=job.location,
                employment_type=job.employment_type,
                score=job.score,
                url=job.url,
                notified=job.notified,
                source_name=job.source_name,
            )
            for job in list_recent_jobs(session)
        ]
    return RecentJobsResponse(items=items)
