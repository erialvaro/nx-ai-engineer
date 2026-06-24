"""Smoke tests for the foundation — liveness works, readiness degrades safely
when the database is unreachable (no real Supabase needed in CI)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_is_ok():
    with TestClient(create_app()) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
        # request-id correlation is echoed back
        assert resp.headers.get("X-Request-ID")


def test_root():
    with TestClient(create_app()) as client:
        assert client.get("/").status_code == 200


def test_ready_reports_database():
    # With no real Supabase configured, /ready degrades (503) but still answers.
    with TestClient(create_app()) as client:
        resp = client.get("/ready")
        assert resp.status_code in (200, 503)
        assert "database" in resp.json()
