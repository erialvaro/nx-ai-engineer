# Policies — Application Security

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Validate and canonicalize all external input at the trust boundary; reject by default.
- Use parameterized queries / prepared statements — never build SQL or commands from strings.
- Enforce authorization on every endpoint/operation; deny by default (no implicit allow).
- Keep secrets in a secret manager/vault, never in code, config files or logs.
- Encode output for its sink (HTML/JS/SQL/shell) to prevent injection/XSS.
- Use strong, current cryptography; never roll your own; rotate keys.
- Scan dependencies for known vulnerabilities; pin and update them.
- Never deserialize untrusted data into rich objects; never `eval` untrusted input.
- Guard outbound requests against SSRF (allow-list hosts; block internal metadata).
- Set secure headers, CSRF protection and rate limiting; fail closed.
- Log security-relevant events without secrets/PII; return generic errors (no stack traces) to clients.
