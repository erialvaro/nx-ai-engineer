# Application Security — Engineering Pack

_Domain: **security**_

Application security baseline aligned to OWASP Top 10 and ASVS: input validation, injection, authz, secrets, crypto, dependencies, SSRF, deserialization, logging and error handling.

## What this pack provides
- **Policies** — enforceable rules for this domain (`policies.md`).
- **Checklists** — review gates (`checklists.md`).
- **Patterns** — recommended approaches (`patterns.md`).
- **Architecture** — structural guidance (`architecture.md`).
- **Context** — the distilled brief fed to agents (`context.md`).
- ADRs, templates and examples under `adr/`, `templates/`, `examples/`.

Install into a project with `nxai pack add security`; the Pack Provider then feeds its policies/checklists/context to the agents working in this domain. This pack contains **no code and no AI** — it organizes knowledge so the model applies it correctly.
