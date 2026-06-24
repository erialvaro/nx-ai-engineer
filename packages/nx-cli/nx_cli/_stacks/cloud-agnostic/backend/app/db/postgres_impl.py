"""Direct PostgreSQL implementation of DatabaseAdapter (the future swap).

Kept intentionally minimal and dependency-light: it validates connectivity with
a stdlib TCP check so the foundation has no hard driver dependency. Wire a real
driver (asyncpg / psycopg) here when you move off Supabase — callers don't change.
"""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse


class PostgresAdapter:
    name = "postgres"

    def __init__(self, database_url: str) -> None:
        self._url = database_url
        parsed = urlparse(database_url)
        self._host = parsed.hostname or "db"
        self._port = parsed.port or 5432

    async def ping(self) -> bool:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=3.0)
            writer.close()
            await writer.wait_closed()
            return True
        except (OSError, asyncio.TimeoutError):
            return False

    async def fetch(self, table: str, filters: dict[str, Any] | None = None
                    ) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "PostgresAdapter.fetch — wire a driver (asyncpg/psycopg) when adopting "
            "plain PostgreSQL. The contract is identical to SupabaseAdapter.")

    async def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("PostgresAdapter.insert — wire a driver to enable.")

    async def close(self) -> None:
        return None
