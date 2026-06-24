# {{project_title}}

A **Cloud-Agnostic** platform foundation scaffolded by
[NX AI Engineer](https://github.com/erialvaro/nx-ai-engineer) (`nxai new`).

It runs the same way **locally via Docker** and on **GCP, Azure, AWS, Oracle
Cloud, a VPS, a dedicated server, Kubernetes or Docker Swarm** — because nothing
depends on a proprietary cloud service. The database is **Supabase** (free tier),
reached through a **decoupled adapter** so it can later be swapped for plain
PostgreSQL without touching application code.

> This is a **foundation only** — no business rules. Add yours on top.

## Stack

| Layer    | Tech                                   | Container |
|----------|----------------------------------------|-----------|
| Backend  | FastAPI (Python) · 12-factor · async   | `backend` |
| Frontend | Next.js (React/TS) · standalone output | `frontend`|
| Database | Supabase (PostgreSQL + Auth + Storage) | external  |
| Runtime  | Docker Compose (dev / override / prod) | —         |

## Quickstart

```bash
cp .env.example .env          # fill SUPABASE_URL + keys (free tier)
make up                       # build + boot the whole stack
make logs                     # tail logs
open http://localhost:{{frontend_port}}     # frontend
open http://localhost:{{backend_port}}/health   # backend health
make down                     # stop
```

## Environments

Config is **100% environment variables** (Twelve-Factor). Per-environment
examples live in [`environments/`](environments/). Compose is layered:

- `docker-compose.yml` — the portable base (works anywhere)
- `docker-compose.override.yml` — local dev (hot reload, bind mounts) — auto-applied
- `docker-compose.prod.yml` — production (restart policies, resource limits)

```bash
make up                       # dev (base + override)
make prod                     # production (base + prod)
```

## Production-readiness

```bash
nxai platform-audit           # Cloud-Agnostic · 12-Factor · Docker · Security ·
                              # Scalability · Observability · Multi-Env · Prod
```

See [`docs/`](docs/) for architecture and ADRs, and
[`supabase/`](supabase/) for migrations, seeds and RLS policies.
