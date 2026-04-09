from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings


def build_scheduler(job_callable) -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_callable, "interval", minutes=settings.search_interval_minutes)
    return scheduler
