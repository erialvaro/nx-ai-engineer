# Policies — Authentication

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Hash passwords with a strong adaptive function (argon2/bcrypt/scrypt).
- Offer/encourage MFA; protect the recovery flow.
- Manage sessions/JWTs safely: short expiry, rotation, secure cookies.
- Throttle and lock out after repeated failures; log auth events (no secrets).
- Prefer OAuth/OIDC for federation; validate tokens and audiences.
