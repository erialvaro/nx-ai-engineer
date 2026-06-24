"""Pick the database implementation from configuration (DB_BACKEND).

This is the only place that knows about concrete backends; everything else
depends on the `DatabaseAdapter` Protocol. See ADR-0002.
"""
from __future__ import annotations

from ..config import Settings
from .adapter import DatabaseAdapter
from .postgres_impl import PostgresAdapter
from .supabase_impl import SupabaseAdapter


def get_adapter(settings: Settings) -> DatabaseAdapter:
    backend = (settings.db_backend or "supabase").lower()
    if backend == "postgres":
        return PostgresAdapter(settings.database_url)
    if backend == "supabase":
        return SupabaseAdapter(settings.supabase_url, settings.supabase_service_role_key)
    raise ValueError(f"unknown DB_BACKEND '{backend}' (use 'supabase' or 'postgres')")
