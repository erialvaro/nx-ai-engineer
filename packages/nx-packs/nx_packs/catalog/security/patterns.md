# Patterns — Application Security

- Defense in depth: validate, authorize and encode at every layer.
- Single input-validation boundary with allow-lists, not block-lists.
- Parameterized data access through a thin repository layer.
- Centralized authorization (policy/middleware) — one place to audit.
- Secret management: inject at runtime from a vault; short-lived credentials.
- Secure-by-default configuration: deny, then explicitly allow.
