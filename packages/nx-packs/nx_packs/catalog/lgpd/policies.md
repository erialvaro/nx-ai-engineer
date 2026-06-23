# Policies — LGPD / Privacy

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Every personal-data processing has a documented lawful basis (consent, contract, legal obligation, legitimate interest).
- Collect the minimum personal data necessary; never collect 'just in case'.
- Never log, print or emit raw PII (mask/pseudonymize in logs, errors and telemetry).
- Encrypt PII at rest and in transit; restrict access by least privilege.
- Enforce tenant/account isolation — never expose one subject's data to another.
- Honor data-subject rights: access, rectification, deletion, portability, objection.
- Apply retention limits; purge or anonymize personal data when no longer needed.
- Sign a DPA with every processor; record international-transfer safeguards.
- Record consent (what, when, version) and provide an easy withdrawal path.
- Run a DPIA for high-risk processing; report breaches to the ANPD/affected subjects without undue delay.
