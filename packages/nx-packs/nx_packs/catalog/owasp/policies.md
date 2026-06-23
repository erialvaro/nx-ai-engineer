# Policies — OWASP Top 10

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- A01 Broken Access Control — enforce centralized authorization.
- A02 Cryptographic Failures — strong crypto, TLS, no secrets in code.
- A03 Injection — parameterized queries and output encoding.
- A04 Insecure Design — threat-model new features.
- A05 Security Misconfiguration — secure-by-default, hardened headers.
- A06 Vulnerable Components — scan and update dependencies.
- A07 Auth Failures — see the authentication pack.
- A08 Integrity Failures — verify packages/CI artifacts; no untrusted deserialization.
- A09 Logging/Monitoring Failures — log security events (no PII).
- A10 SSRF — allow-list outbound hosts.
