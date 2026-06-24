"""Supabase implementation of DatabaseAdapter — plain HTTP (PostgREST) via httpx.

No proprietary SDK: just REST calls, so the platform stays cloud-agnostic and
Supabase remains an implementation detail. The service-role key is server-side
only and bypasses RLS for trusted backend operations.
"""
from __future__ import annotations

from typing import Any

import httpx


class SupabaseAdapter:
    name = "supabase"

    def __init__(self, url: str, service_role_key: str) -> None:
        self._base = url.rstrip("/") + "/rest/v1"
        self._client = httpx.AsyncClient(
            base_url=self._base,
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    async def ping(self) -> bool:
        try:
            # PostgREST root responds 200 with the OpenAPI description.
            resp = await self._client.get("/")
            return resp.status_code < 500
        except httpx.HTTPError:
            return False

    async def fetch(self, table: str, filters: dict[str, Any] | None = None
                    ) -> list[dict[str, Any]]:
        params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
        params.setdefault("select", "*")
        resp = await self._client.get(f"/{table}", params=params)
        resp.raise_for_status()
        return resp.json()

    async def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(
            f"/{table}", json=row, headers={"Prefer": "return=representation"})
        resp.raise_for_status()
        data = resp.json()
        return data[0] if isinstance(data, list) and data else data

    async def close(self) -> None:
        await self._client.aclose()
