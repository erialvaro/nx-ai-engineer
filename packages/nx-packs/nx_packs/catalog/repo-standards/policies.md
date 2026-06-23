# Policies — Repository Standards

Enforceable rules for repository hygiene.

- Every repository has a README, a LICENSE, CONTRIBUTING, CODE_OF_CONDUCT and SECURITY.md.
- CI runs the test suite on every push and pull request; merges are gated on green.
- Use issue templates and a pull-request template with a review checklist.
- Follow Semantic Versioning, keep a CHANGELOG, and automate releases by tag.
- Protect the default branch: require review + green CI before merge.
- Pin/lock dependencies and scan them for known vulnerabilities.
- Never commit secrets; use repository/organization secrets.
- Route reviews with CODEOWNERS where the team is non-trivial.
