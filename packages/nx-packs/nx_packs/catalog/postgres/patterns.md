# Patterns — PostgreSQL

- Repository pattern — isolate data access behind an interface.
- Unit of Work — group writes into one transaction boundary.
- Soft delete — `deleted_at` + a partial index `WHERE deleted_at IS NULL`.
- Tenant isolation — `tenant_id` on every row; filter on every query; consider RLS.
- Audit — append-only audit table / triggers recording who/when (never PII values).
- Versioning — optimistic concurrency via a `version`/`updated_at` column.
