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

- Create the GitHub repository and push. (Done — `erialvaro/nx-ai-engineer`.)
- Create a GitHub **environment** named `pypi` (Settings → Environments). Optional:
  add a required-reviewer protection rule so a human approves each publish.
- Choose **one** PyPI auth method below. The workflow needs no change — it uses
  Trusted Publishing by default and falls back to the token only if the secret exists.

### Option A — Trusted Publishing / OIDC (recommended, no secrets)

The platform ships **10 distributions** (the `nx-ai-engineer` metapackage + the 9
`nx-*` packages). Since none exist on PyPI yet, register a **pending publisher** for
each, once, at <https://pypi.org/manage/account/publishing/>:

- **PyPI Project Name:** the distribution name — one of: `nx-ai-engineer`
  (the metapackage), `nxai-core`, `nxai-workflow`, `nxai-sdk`, `nxai-packs`,
  `nxai-providers`, `nxai-obsidian`, `nxai-knowledge`, `nxai-runtime`, `nxai-cli`
- **Owner:** `erialvaro` · **Repository:** `nx-ai-engineer`
- **Workflow name:** `release.yml` · **Environment:** `pypi`

(All 10 names were verified available. The PyPI distribution names use the `nxai-`
prefix; the import modules stay `nx_*` — e.g. `pip install nxai-core` ships
`import nx_core`.) After registration, tagging a release
publishes with no token — GitHub mints a short-lived OIDC credential per project.

### Option B — API token (simplest, 1 secret)

1. Create a PyPI API token at <https://pypi.org/manage/account/token/> (account-
   scoped for the first publish; re-scope to per-project tokens afterwards).
2. Add it as a secret named `PYPI_API_TOKEN` in the **`pypi`** environment
   (or repository) of `erialvaro/nx-ai-engineer`:
   ```bash
   gh secret set PYPI_API_TOKEN --repo erialvaro/nx-ai-engineer --env pypi
   ```
   The release workflow detects the secret and uses it instead of OIDC.

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
   - builds sdists + wheels for the metapackage and all 9 packages (`twine check`),
   - publishes them to PyPI via **Trusted Publishing (OIDC)** — or the
     `PYPI_API_TOKEN` secret if set (token fallback),
   - creates a GitHub Release with generated notes and the artifacts.

## Publication checklist

- [ ] Quality Gate green (tests, cycles, unused-imports, CLI, API, docs)
- [ ] `verify_packages.py` green (declared **and** real-import graphs)
- [ ] `bump_version.py --check` reports a single agreed version
- [ ] CHANGELOG has a dated section for the version
- [ ] README / RELEASE_NOTES reflect the version and command surface
- [ ] No third-party runtime dependency added to the core (stdlib-only)
- [ ] `pypi` GitHub environment exists
- [ ] PyPI auth configured — **either** trusted publishers for all 10 projects
      (Option A) **or** the `PYPI_API_TOKEN` secret (Option B)
- [ ] Tag `v<version>` pushed → release workflow green → packages on PyPI + GitHub Release

## Verifying a published release

```bash
pip install nx-ai-engineer==<version>
nxai version      # matches the tag
nxai doctor       # all packages aligned
```
