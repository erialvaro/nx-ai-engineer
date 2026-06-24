# Security — Elasticsearch

- Least-privilege database roles; no app using a superuser.
- Never build queries from string concatenation — parameterize.
- Encrypt sensitive columns; never store secrets/PII in plaintext.
- Audit access to sensitive tables; never log raw PII.
