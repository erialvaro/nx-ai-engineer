# Supabase

The database for {{project_title}} (free tier to start). Everything here is
plain SQL, so it applies equally to **Supabase** and **self-hosted PostgreSQL**
— keeping the platform cloud-agnostic.

| File                       | Purpose                                            |
|----------------------------|----------------------------------------------------|
| `migrations/0001_init.sql` | Base schema + **Row Level Security** enabled       |
| `policies.sql`             | RLS policies (who can read/write each row)         |
| `seed.sql`                 | Non-secret sample/reference data                   |

## Apply

```bash
# Supabase: Settings > Database > Connection string  -> SUPABASE_DB_URL
export SUPABASE_DB_URL="postgresql://postgres:...@db.your-project.supabase.co:5432/postgres"
make migrate            # runs scripts/migrate.sh over migrations/*.sql
psql "$SUPABASE_DB_URL" -f supabase/policies.sql
psql "$SUPABASE_DB_URL" -f supabase/seed.sql
```

## Keys (from Supabase > Settings > API)

- `SUPABASE_ANON_KEY` — public, client-side (respects RLS).
- `SUPABASE_SERVICE_ROLE_KEY` — server-side only, **bypasses RLS** — never ship
  to the frontend. The backend keeps it in `.env`.
