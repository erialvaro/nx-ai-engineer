# Context — Authentication

Authenticate strongly and manage sessions safely; never store plaintext credentials; pair with the authorization controls in the security pack.

## Non-negotiables
- Hash passwords with a strong adaptive function (argon2/bcrypt/scrypt).
- Offer/encourage MFA; protect the recovery flow.
- Manage sessions/JWTs safely: short expiry, rotation, secure cookies.
- Throttle and lock out after repeated failures; log auth events (no secrets).
- Prefer OAuth/OIDC for federation; validate tokens and audiences.

## Always verify
- Passwords hashed (argon2/bcrypt)
- MFA available + recovery protected
- Sessions/JWTs short-lived + rotated
- Lockout/throttling present
- OAuth/OIDC tokens validated
