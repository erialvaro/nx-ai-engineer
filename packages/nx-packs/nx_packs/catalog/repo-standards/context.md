# Context — Repository Standards

A healthy repository has clear governance and automation: README, LICENSE,
CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue/PR templates, CI on every push,
and SemVer releases. When setting up or reviewing a repo, ensure these exist —
run `nxai scaffold` to lay them down.

## Non-negotiables
- Every repository has a README, a LICENSE, CONTRIBUTING, CODE_OF_CONDUCT and SECURITY.md.
- CI runs the test suite on every push and pull request; merges are gated on green.
- Use issue templates and a pull-request template with a review checklist.
- Follow Semantic Versioning, keep a CHANGELOG, and automate releases by tag.
- Protect the default branch: require review + green CI before merge.

## Always verify
- README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY present
- CI workflow present and green on the change
- Issue templates + PR template present
- CHANGELOG updated; SemVer tag for releases
- Default-branch protection (review + CI required)
