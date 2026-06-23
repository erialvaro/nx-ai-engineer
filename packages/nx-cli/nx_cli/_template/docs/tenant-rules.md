# Data Isolation / Multi-Tenant Rules

> Generic guide. It only applies if the project is multi-tenant (or otherwise
> partitions data by owner/account). If so, declare the invariant in
> `config.json > domain_rules` so the planner and task files surface it on every
> relevant change. If the project is single-tenant, this file can stay as
> reference.

## Core invariant
Every query, mutation and cache key that touches tenant-scoped data MUST be
filtered by the current tenant/owner. No code path may read or write another
tenant's data.

## Rules
- Always derive the tenant from the authenticated context, never from
  client-supplied input alone.
- Every tenant-scoped table carries the scoping column; every repository method
  applies it. No raw cross-tenant queries.
- Background jobs and AI/RAG retrieval must carry and enforce tenant scope.
- Caches, search indexes and embeddings are namespaced per tenant.
- Tests must include a cross-tenant negative case (tenant A cannot see B).

## Review focus
- Any new query/endpoint: confirm the tenant filter is present and enforced.
- Any new cache/index/embedding: confirm namespacing.
