# Privacy / LGPD / PII Handling

> Generic privacy guide (aligned with LGPD/GDPR principles). Applies when the
> project stores personal data. Declare specifics in `config.json >
> domain_rules`.

## Principles
- **Minimization:** collect and store only the personal data you need.
- **Purpose limitation:** use data only for its stated purpose.
- **Security:** encrypt in transit; protect at rest; least-privilege access.
- **Transparency & rights:** support access, correction and deletion requests.

## Rules for changes
- Never log PII (emails, documents, phone numbers, tokens). Mask if needed.
- Never expose personal data across tenants/accounts (see `tenant-rules.md`).
- New data fields holding PII must be documented and access-controlled.
- Deletion/anonymization paths must actually remove or anonymize the data.
- Third-party/AI calls must not leak PII beyond what is necessary and consented.

## Review focus
- New fields: is any of it personal data? Is it minimized and protected?
- New logs/telemetry: do they contain PII?
- New integrations: what personal data leaves the system, and why?
