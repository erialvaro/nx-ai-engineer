# Policies — Multi-Tenancy

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Every query/command carries the tenant id; deny cross-tenant by default.
- Isolation model (row-level / schema / database) is explicit and enforced.
- No global mutable state shared across tenants.
- Tenant context is set at the boundary and propagated, never inferred.
- Noisy-neighbor limits protect one tenant from another.
