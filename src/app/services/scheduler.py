from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.services.collector import MultiSourceCollector
from app.services.run_jobs import run_collection_cycle
from app.utils.http import build_http_client


RUNTIME_SCHEDULER: AsyncIOScheduler | None = None


def run_scheduled_cycle():
    settings = get_settings(refresh=True)
    sync_scheduler_interval(RUNTIME_SCHEDULER, settings=settings)
    collector = build_runtime_collector(settings)
    return run_collection_cycle(collector)


def build_runtime_collector(settings):
    return MultiSourceCollector.build_from_settings(settings, build_http_client)


def build_scheduler(job_callable, interval_minutes: int) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_callable, "interval", minutes=interval_minutes, id="job-search-cycle")
    return scheduler


def set_runtime_scheduler(scheduler: AsyncIOScheduler) -> None:
    global RUNTIME_SCHEDULER
    RUNTIME_SCHEDULER = scheduler


def sync_scheduler_interval(scheduler: AsyncIOScheduler | None, settings=None) -> None:
    if scheduler is None:
        return

    current_settings = settings or get_settings(refresh=True)
    job = scheduler.get_job("job-search-cycle")
    if job is None:
        return

    current_seconds = int(job.trigger.interval.total_seconds())
    desired_seconds = current_settings.search_interval_minutes * 60
    if current_seconds != desired_seconds:
        job.reschedule(trigger="interval", minutes=current_settings.search_interval_minutes)
