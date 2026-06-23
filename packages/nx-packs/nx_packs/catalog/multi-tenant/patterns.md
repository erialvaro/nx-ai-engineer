# Patterns — Multi-Tenancy

- Tenant-scoped repository that refuses unscoped queries.
- Row-level security or schema-per-tenant.
- Tenant id derived from the authenticated principal, not the payload.
