# Checklist — Application Security

Review gate for changes touching this domain.

- [ ] Change mapped against OWASP Top 10 (A01–A10)
- [ ] All input validated/encoded at the boundary
- [ ] Queries parameterized; no string-built SQL/commands
- [ ] Authorization checked on every new endpoint/operation
- [ ] No secrets in code/config/logs; pulled from a vault
- [ ] Dependencies scanned; no known-vulnerable versions added
- [ ] TLS enforced; strong crypto; no custom crypto
- [ ] Security headers + CSRF + rate limiting present
- [ ] No untrusted deserialization / eval
- [ ] SSRF guard on outbound requests
- [ ] Errors are generic to clients; security events logged (no PII/secrets)
