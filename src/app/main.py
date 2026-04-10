from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.api.ui import router as ui_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.scheduler import build_scheduler, run_scheduled_cycle, set_runtime_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = app.state.scheduler
    if not scheduler.running:
        scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="busca-vagas", lifespan=lifespan)
    settings = get_settings()
    scheduler = build_scheduler(run_scheduled_cycle, interval_minutes=settings.search_interval_minutes)
    set_runtime_scheduler(scheduler)
    app.state.scheduler = scheduler
    app.mount("/static", StaticFiles(directory="src/app/static"), name="static")

    app.include_router(health_router)
    app.include_router(admin_router)
    app.include_router(ui_router)
    return app


app = create_app()
