# Architecture — LGPD / Privacy

Separate storage zones by sensitivity; PII lives in an encrypted, access-controlled store with a tenant boundary on every query. Logs, caches and analytics receive pseudonymized or masked values only. A retention job and a deletion path operate on every personal-data store.
