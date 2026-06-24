"""The database contract — the ONLY thing application code may import.

Concrete backends (Supabase, PostgreSQL, an in-memory fake for tests) implement
this Protocol. Swapping backends never touches callers. See ADR-0002.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DatabaseAdapter(Protocol):
    name: str

    async def ping(self) -> bool:
        """Return True if the database is reachable (used by /ready)."""
        ...

    async def fetch(self, table: str, filters: dict[str, Any] | None = None
                    ) -> list[dict[str, Any]]:
        """Return rows from `table` matching `filters` (equality)."""
        ...

    async def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        """Insert `row` into `table` and return the stored record."""
        ...

    async def close(self) -> None:
        """Release any held resources (connections/clients)."""
        ...
