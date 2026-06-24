"""Liveness and readiness endpoints (observability / orchestration).

  GET /health  — liveness: the process is up (used by Docker HEALTHCHECK).
  GET /ready   — readiness: dependencies (the database) are reachable.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict:
    adapter = request.app.state.db
    ok = await adapter.ping()
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if ok else "degraded", "database": adapter.name}
