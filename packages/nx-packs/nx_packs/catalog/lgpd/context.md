# Context — LGPD / Privacy

When a change touches personal data (PII) you must protect it end to end: collect the minimum, store it encrypted and tenant-scoped, never log raw PII, honor data-subject rights, and delete it on schedule. Treat every personal-data flow as auditable.

## Non-negotiables
- Every personal-data processing has a documented lawful basis (consent, contract, legal obligation, legitimate interest).
- Collect the minimum personal data necessary; never collect 'just in case'.
- Never log, print or emit raw PII (mask/pseudonymize in logs, errors and telemetry).
- Encrypt PII at rest and in transit; restrict access by least privilege.
- Enforce tenant/account isolation — never expose one subject's data to another.

## Always verify
- PII inventory updated for the changed data flow
- Lawful basis documented for new/changed processing
- PII encrypted at rest and in transit
- Access restricted by least privilege and tenant scope
- Logs/telemetry/errors contain no raw PII
