"""Application settings — Twelve-Factor: every value comes from the environment.

Nothing is hardcoded; secrets are injected at runtime (.env locally, a secret
manager in production). Cloud-agnostic: no provider SDK is referenced here.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "info"
    secret_key: str = "changeme"

    # Database selection: "supabase" (default) or "postgres" (future swap).
    db_backend: str = "supabase"

    # Supabase (used when db_backend == "supabase")
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Direct PostgreSQL (used when db_backend == "postgres")
    database_url: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
