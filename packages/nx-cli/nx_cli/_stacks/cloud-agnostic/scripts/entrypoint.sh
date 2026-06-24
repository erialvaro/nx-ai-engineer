#!/usr/bin/env sh
# Backend container entrypoint. Cloud-agnostic: no provider-specific calls.
set -e

: "${APP_ENV:=development}"
echo "[entrypoint] starting backend (APP_ENV=$APP_ENV)"

# Optionally wait for a direct Postgres when DB_BACKEND=postgres.
if [ "${DB_BACKEND:-supabase}" = "postgres" ] && [ -n "${DATABASE_URL:-}" ]; then
  ./scripts/wait-for.sh "${DATABASE_HOST:-db}" "${DATABASE_PORT:-5432}" || true
fi

exec "$@"
