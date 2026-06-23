# Context — OWASP Top 10

Map every change to the OWASP Top 10 and ensure the matching control is present.

## Non-negotiables
- A01 Broken Access Control — enforce centralized authorization.
- A02 Cryptographic Failures — strong crypto, TLS, no secrets in code.
- A03 Injection — parameterized queries and output encoding.
- A04 Insecure Design — threat-model new features.
- A05 Security Misconfiguration — secure-by-default, hardened headers.

## Always verify
- A01–A10 each have an explicit control in this change
- Authorization centralized
- Dependencies scanned
- Security headers set
- SSRF guard present
