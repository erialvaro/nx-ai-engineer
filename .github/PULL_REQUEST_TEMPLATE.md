<!-- Thanks for contributing to NX AI Engineer! -->

## What & why
<!-- What does this change and why? Link issues with "Closes #123". -->

## Type
- [ ] Fix (patch)
- [ ] Feature (minor, additive)
- [ ] Breaking change (major) — includes a migration note
- [ ] Docs / chore

## Checklist
- [ ] `python scripts/quality_gate.py` passes (tests, no cycles, no unused imports, CLI/API, docs)
- [ ] `python scripts/verify_packages.py` passes (acyclic package graph)
- [ ] No new third-party runtime dependency (the core is **stdlib-only**)
- [ ] No behavior removed; public CLI/SDK surface preserved (or breaking change documented)
- [ ] Docs updated (CHANGELOG + relevant guide/ADR) if behavior or surface changed
- [ ] The Knowledge Engine still only organizes (never reasons); the Brain never stores code

## Notes for reviewers
<!-- Anything that needs special attention. -->
