# Context — Multi-Tenancy

Every data access is tenant-scoped; cross-tenant access is impossible by construction. Builds on the tenant-rules project doc.

## Non-negotiables
- Every query/command carries the tenant id; deny cross-tenant by default.
- Isolation model (row-level / schema / database) is explicit and enforced.
- No global mutable state shared across tenants.
- Tenant context is set at the boundary and propagated, never inferred.
- Noisy-neighbor limits protect one tenant from another.

## Always verify
- Tenant scope on every query
- Isolation model enforced
- No cross-tenant shared state
- Tenant context propagated
- Per-tenant limits
