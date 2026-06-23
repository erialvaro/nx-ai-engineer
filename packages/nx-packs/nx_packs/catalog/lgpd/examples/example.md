# Example — LGPD / Privacy

A tenant-scoped read: every query filters by `tenant_id` from the request context; a shared helper refuses to build a personal-data query without a tenant scope, so cross-tenant access is impossible by construction.
