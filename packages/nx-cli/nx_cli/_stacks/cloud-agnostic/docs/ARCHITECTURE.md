# Architecture — {{project_title}}

A cloud-agnostic, Twelve-Factor foundation. Two stateless app containers talk to
an external managed database (Supabase) through a decoupled adapter.

```
            ┌────────────┐        ┌────────────┐
  browser → │  frontend  │  HTTP  │  backend   │  adapter   ┌──────────┐
            │ (Next.js)  │ ─────► │ (FastAPI)  │ ─────────► │ Supabase │
            └────────────┘        └────────────┘            │ (or PG)  │
                  :3000                 :8000                └──────────┘
                     \___ docker-compose (appnet) ___/        external
```

## Principles

1. **Cloud-agnostic** — nothing depends on a proprietary cloud SDK. The only
   external dependency is the database, reached over plain HTTP/SQL.
2. **Twelve-Factor** — all config is environment variables; logs go to stdout;
   dev/prod parity via layered compose files; stateless processes.
3. **Decoupled persistence** — application code depends on the
   [`DatabaseAdapter`](../backend/app/db/adapter.py) Protocol, not on Supabase.
   Swapping to plain PostgreSQL is an env flag (`DB_BACKEND=postgres`), no code
   change. See [ADR-0002](adr/ADR-0002-supabase-decoupled-adapter.md).
4. **Observability built in** — structured JSON logs, request-id correlation,
   `/health` + `/ready` endpoints from day one.

## Portability targets

The same `docker-compose.yml` (+ `.prod.yml`) runs on Docker locally, a VPS, a
dedicated server, Docker Swarm, and any managed container service on GCP / Azure
/ AWS / Oracle Cloud. For Kubernetes, translate the compose with `kompose` or the
provided manifests (follow-up). See
[CLOUD_AGNOSTIC.md](CLOUD_AGNOSTIC.md).
