from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="busca-vagas")
    app.include_router(health_router)
    app.include_router(admin_router)
    return app


app = create_app()
