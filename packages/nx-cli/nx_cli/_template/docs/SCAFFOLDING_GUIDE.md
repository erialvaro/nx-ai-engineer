# Scaffolding Guide — `nxai new`

NX AI Engineer is not only a library you add to a project — it can **create the
project**. `nxai new` is the `create-next-app` / `django-admin startproject`
moment for AI-native platforms: one command lays down a complete,
**cloud-agnostic** foundation, then makes it AI-ready.

```bash
nxai new my-platform
cd my-platform
cp .env.example .env        # fill Supabase URL + keys (free tier)
make up                     # boot the whole stack via Docker Compose
nxai platform-audit         # verify production-readiness
```

## What gets generated

The default stack — `cloud-agnostic` — is a **foundation only** (no business
rules), engineered to run identically on Docker locally and on GCP, Azure, AWS,
Oracle Cloud, a VPS, a dedicated server, Kubernetes or Docker Swarm:

```
my-platform/
  backend/            FastAPI · 12-factor · structured logs · request-id
    app/db/adapter.py   decoupled DatabaseAdapter (Supabase today, PG tomorrow)
    Dockerfile          multi-stage · non-root · healthcheck
  frontend/           Next.js (standalone output) · Dockerfile
  docker-compose.yml          portable base (runs anywhere)
  docker-compose.override.yml local dev (hot reload)
  docker-compose.prod.yml     production (restart + resource limits)
  Makefile            up/down/logs/build/shell/migrate/lint/test/clean
  .env.example        all config as environment variables
  environments/       per-environment examples (dev/staging/prod)
  configs/ scripts/ volumes/ logs/
  supabase/           migrations (RLS), policies, seed
  docs/               architecture + ADRs
  .ai-project-assistant/   the AI working home (added automatically)
```

## How it works

- **Stack templates** live in `nx_cli/_stacks/<stack>/` and ship as package data.
- **Variable rendering**: `{{ project_name }}`, `{{ project_slug }}`,
  `{{ project_title }}`, `{{ backend_port }}`, `{{ frontend_port }}` are
  substituted in file contents.
- **Dotfile convention**: a template path beginning `dot.` becomes a real
  dotfile (`dot.gitignore` → `.gitignore`) so dotfiles survive wheel packaging.
- After scaffolding, `nxai new` runs `nxai init` (the `.ai-project-assistant`
  home) and a `platform-audit`.

## Options

```
nxai new <name> [--stack cloud-agnostic] [--path DIR]
                [--backend-port 8000] [--frontend-port 3000]
                [--force] [--no-init] [--no-audit]
```

## The platform audit

`nxai platform-audit` statically scores a project across eight production
dimensions — **Cloud-Agnostic · Twelve-Factor · Docker · Security · Scalability
· Observability · Multi-Environment · Production-Ready** — printing PASS / WARN /
FAIL per check. A freshly generated foundation comes out green. Use `--strict`
to fail on warnings (good for CI).

## Adding a stack

Drop a new folder under `nx_cli/_stacks/<name>/` containing a `stack.json` and
the template files (using the `{{var}}` and `dot.` conventions). It is picked up
automatically — `nxai new <project> --stack <name>`. Optional service layers
(Redis, Nginx, worker, scheduler, Mailhog, MinIO, PgAdmin) and deeper
observability (OpenTelemetry) are intended as follow-up overlays on this base.
