# Patterns — LGPD / Privacy

- Data classification: tag fields as public / internal / personal / sensitive and drive controls from the tag.
- Field-level encryption or tokenization for sensitive PII.
- Pseudonymization: store a stable surrogate id; keep the mapping isolated.
- Tenant-scoped queries: every read/write carries the tenant id; deny cross-tenant by default.
- Audit log of access to personal data — record who/when/why, never the PII values.
- Soft-delete + scheduled hard-purge to satisfy deletion + retention together.
