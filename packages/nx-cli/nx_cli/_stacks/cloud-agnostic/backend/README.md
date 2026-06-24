# Backend — {{project_title}}

FastAPI service. Twelve-Factor, async, structured logs, request-id correlation,
and a **decoupled database adapter** (Supabase today, plain PostgreSQL tomorrow
via `DB_BACKEND` — no code change).

## Layout

```
app/
  main.py            # app factory: logging, middleware, routers, lifespan
  config.py          # env-only settings (pydantic-settings)
  logging_setup.py   # JSON structured logging to stdout
  middleware.py      # X-Request-ID correlation
  routers/health.py  # /health (liveness) + /ready (readiness)
  db/
    adapter.py       # DatabaseAdapter Protocol (the only thing app code imports)
    supabase_impl.py # Supabase REST implementation (httpx)
    postgres_impl.py # direct PostgreSQL implementation (future swap)
    factory.py       # picks the impl from DB_BACKEND
tests/test_health.py
```

## Run

```bash
# via Docker (recommended): from the project root
make up
# or locally:
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -q
```

Endpoints: `GET /` · `GET /health` · `GET /ready` · docs at `/docs`.
