# ADR-0001: Repository Standards baseline

- **Status:** Accepted
- **Domain:** repo-standards

## Context
Open-source repository standards: governance files, CI/CD, issue/PR templates, security policy and a conventional structure. Applied with `nxai scaffold`.

## Decision
Adopt the governance files, CI and templates provided by this pack as the repo baseline,
applied via `nxai scaffold`.

## Consequences
Repos are reviewed against `checklists.md`;
missing governance/CI blocks an open-source release.
