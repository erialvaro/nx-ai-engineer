#!/usr/bin/env sh
# Apply SQL migrations in supabase/migrations/ in order.
# Works against Supabase OR plain Postgres via psql + a connection string.
#   DB_BACKEND=supabase   -> set SUPABASE_DB_URL (Settings > Database > Connection string)
#   DB_BACKEND=postgres   -> uses DATABASE_URL
set -e

conn="${SUPABASE_DB_URL:-${DATABASE_URL:-}}"
if [ -z "$conn" ]; then
  echo "error: set SUPABASE_DB_URL (or DATABASE_URL) to run migrations" >&2
  exit 1
fi

for f in supabase/migrations/*.sql; do
  [ -f "$f" ] || continue
  echo "[migrate] applying $f"
  psql "$conn" -v ON_ERROR_STOP=1 -f "$f"
done

# Apply RLS policies and seed AFTER the schema exists. Without policies, the
# RLS-enabled tables deny all access — so this step is required, not optional.
for extra in supabase/policies.sql supabase/seed.sql; do
  [ -f "$extra" ] || continue
  echo "[migrate] applying $extra"
  psql "$conn" -v ON_ERROR_STOP=1 -f "$extra"
done
echo "[migrate] done"
