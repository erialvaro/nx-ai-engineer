"""Application factory — wires logging, request-id, routers and the DB adapter.

Foundation only: a root route plus health/readiness. Add your routers under
`app/routers/` and your domain logic on top of the database adapter.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db.factory import get_adapter
from .logging_setup import configure_logging
from .middleware import RequestIdMiddleware
from .routers import health

log = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.settings = settings
    app.state.db = get_adapter(settings)
    log.info("startup: env=%s db_backend=%s", settings.app_env, settings.db_backend)
    try:
        yield
    finally:
        await app.state.db.close()
        log.info("shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="{{project_title}} API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    # CORS is env-driven and secure by default: an empty allowlist permits only
    # same-origin requests. Set CORS_ALLOW_ORIGINS per environment.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)

    @app.get("/")
    async def root() -> dict:
        return {"service": "{{project_slug}}", "status": "ok"}

    return app


app = create_app()
