# Checklist — Authentication

Review gate for changes touching this domain.

- [ ] Passwords hashed (argon2/bcrypt)
- [ ] MFA available + recovery protected
- [ ] Sessions/JWTs short-lived + rotated
- [ ] Lockout/throttling present
- [ ] OAuth/OIDC tokens validated
