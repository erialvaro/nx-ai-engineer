# Releasing NX AI Engineer

The platform is **9 stdlib-only packages** released together under one version,
following [Semantic Versioning](https://semver.org). Releases are automated by a
tag-driven GitHub Actions workflow (`.github/workflows/release.yml`).

## Versioning policy

- **patch** `1.0.x` — fixes, docs, internal improvements. Backward compatible.
- **minor** `1.x.0` — new, additive capabilities (new commands, packs, providers).
  Backward compatible.
- **major** `x.0.0` — a breaking change to the CLI/SDK/provider contract. Ships
  with a migration note in `MIGRATION_GUIDE.md` and the CHANGELOG.

## One-time setup

- Create the GitHub repository and push.
- Add a `PYPI_API_TOKEN` repository secret (a PyPI API token scoped to the
  project). The release workflow publishes with it via `twine`.
- (Optional, recommended later) switch to PyPI **trusted publishing** (OIDC) per
  package and drop the token.

## Cutting a release

1. **Green build** — `python scripts/quality_gate.py` and
   `python scripts/verify_packages.py` must pass on `main`.
2. **Bump the version everywhere** (all `__init__` + every `pyproject.toml` +
   pinned intra-workspace deps, kept in lock-step):
   ```bash
   python scripts/bump_version.py 1.1.0
   python scripts/bump_version.py --check     # confirms every string agrees
   ```
3. **Update docs** — move the `[Unreleased]`/top notes into a dated
   `## [1.1.0]` section of `CHANGELOG.md`; refresh `RELEASE_NOTES.md` and
   `ROADMAP.md` if needed.
4. **Commit & tag** — the tag must equal the version (the workflow guards this):
   ```bash
   git commit -am "release: 1.1.0"
   git tag v1.1.0
   git push && git push --tags
   ```
5. **Automation takes over** (`release.yml` on the `v*` tag):
   - re-runs the Quality Gate (release is blocked if it fails),
   - verifies the tag matches the package version,
   - builds sdists + wheels for the metapackage and all 9 packages,
   - `twine check` then `twine upload` to PyPI,
   - creates a GitHub Release with generated notes and the artifacts.

## Publication checklist

- [ ] Quality Gate green (tests, cycles, unused-imports, CLI, API, docs)
- [ ] `verify_packages.py` green (declared **and** real-import graphs)
- [ ] `bump_version.py --check` reports a single agreed version
- [ ] CHANGELOG has a dated section for the version
- [ ] README / RELEASE_NOTES reflect the version and command surface
- [ ] No third-party runtime dependency added to the core (stdlib-only)
- [ ] `PYPI_API_TOKEN` secret configured
- [ ] Tag `v<version>` pushed → release workflow green → package on PyPI + GitHub Release

## Verifying a published release

```bash
pip install nx-ai-engineer==<version>
nxai version      # matches the tag
nxai doctor       # all packages aligned
```
