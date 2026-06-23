# ADR-0001: LGPD / Privacy baseline

- **Status:** Accepted
- **Domain:** privacy

## Context
Brazilian LGPD and general privacy/PII handling: lawful basis, data-subject rights, minimization, tenant isolation, retention and incident response.

## Decision
Adopt field-level encryption + pseudonymization for sensitive PII, tenant-scoped data access, and a soft-delete + scheduled-purge retention model.

## Consequences
Changes in this domain are reviewed against `checklists.md`; violations of `policies.md` block delivery.
