# Test guidance — LGPD / Privacy

Turn each checklist item into a concrete, automated test where possible (unit/integration/contract). Examples to implement for your stack:

- Assert logs/telemetry for a PII-handling path contain no raw PII values.
- Assert a personal-data query without a tenant scope is rejected.
- Assert the deletion path removes the subject across all stores.
