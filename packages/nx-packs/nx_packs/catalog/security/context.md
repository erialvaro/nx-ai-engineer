# Context — Application Security

Treat all external input as hostile and deny by default. Validate input at the boundary, use parameterized queries, check authorization on every request, keep secrets out of code, and never leak internals in errors. Map every change against the OWASP Top 10.

## Non-negotiables
- Validate and canonicalize all external input at the trust boundary; reject by default.
- Use parameterized queries / prepared statements — never build SQL or commands from strings.
- Enforce authorization on every endpoint/operation; deny by default (no implicit allow).
- Keep secrets in a secret manager/vault, never in code, config files or logs.
- Encode output for its sink (HTML/JS/SQL/shell) to prevent injection/XSS.

## Always verify
- Change mapped against OWASP Top 10 (A01–A10)
- All input validated/encoded at the boundary
- Queries parameterized; no string-built SQL/commands
- Authorization checked on every new endpoint/operation
- No secrets in code/config/logs; pulled from a vault
