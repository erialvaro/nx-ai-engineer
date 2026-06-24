# ADR-0002 — Supabase via a Decoupled Database Adapter

- **Status:** Accepted
- **Context:** The initial database is **Supabase** (free tier) for auth,
  PostgreSQL, storage and RLS. But the platform must not be wedded to it — a
  future move to plain PostgreSQL (self-hosted or managed) must cost no
  application changes.

## Decision

Application code depends only on the `DatabaseAdapter` **Protocol**
([`backend/app/db/adapter.py`](../../backend/app/db/adapter.py)). Concrete
implementations — `SupabaseAdapter` (REST/PostgREST over HTTP) and
`PostgresAdapter` (direct SQL) — are selected at runtime by the `DB_BACKEND`
environment variable via a small factory. No module imports the Supabase client
directly.

## Consequences

- ➕ Swapping backends is an env flag (`DB_BACKEND=postgres`), not a refactor.
- ➕ Supabase stays an implementation detail; the rest of the app is testable
  against an in-memory/fake adapter.
- ➕ Stays cloud-agnostic: Supabase is open-source and self-hostable; the adapter
  speaks plain HTTP/SQL.
- ➖ A thin abstraction to maintain — kept deliberately minimal (CRUD + query).
