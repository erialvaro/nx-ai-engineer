# ADR-0001: Application Security baseline

- **Status:** Accepted
- **Domain:** security

## Context
Application security baseline aligned to OWASP Top 10 and ASVS: input validation, injection, authz, secrets, crypto, dependencies, SSRF, deserialization, logging and error handling.

## Decision
Adopt a centralized authorization layer, a single input-validation boundary, parameterized data access, and vault-injected secrets as the security baseline.

## Consequences
Changes in this domain are reviewed against `checklists.md`; violations of `policies.md` block delivery.
