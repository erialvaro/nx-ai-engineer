# scripts/

Portable shell helpers (POSIX `sh`, no provider lock-in).

| Script          | Purpose                                             |
|-----------------|-----------------------------------------------------|
| `entrypoint.sh` | Backend container entrypoint (optional DB wait)     |
| `wait-for.sh`   | Block until a `host:port` is reachable              |
| `migrate.sh`    | Apply `supabase/migrations/*.sql` via `psql`        |

Invoked by the `Makefile` and the backend `Dockerfile`.
