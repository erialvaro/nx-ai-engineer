# Releasing NX AI Engineer

The platform ships as **one self-contained distribution** — `nx-ai-engineer` — a
single wheel that bundles every `nx_*` module. For development the code lives in
**9 acyclic, stdlib-only packages** under `packages/` (each with its own
`pyproject`, tests and dependency edges, verified by `scripts/verify_packages.py`);
for distribution the root `pyproject.toml` builds them all into one artifact. So
`pip install nx-ai-engineer` carries the whole platform — there are **no
sub-distributions on PyPI**. Versioning follows
[SemVer](https://semver.org); releases are automated by a tag-driven GitHub
Actions workflow (`.github/workflows/release.yml`).

> **Why one package?** PyPI rate-limits *new project creation* per source IP, and
> GitHub Actions runners share IPs — so publishing many brand-new projects at once
> reliably hits `429 Too many new projects created`. A single distribution sidesteps
> this entirely: every release after the first is just an *update* to an existing
> project, which is never rate-limited.

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

There is **one distribution** to publish: `nx-ai-engineer`. Register a single
trusted publisher, once, at <https://pypi.org/manage/account/publishing/>:

- **PyPI Project Name:** `nx-ai-engineer`
- **Owner:** `erialvaro` · **Repository:** `nx-ai-engineer`
- **Workflow name:** `release.yml` · **Environment:** `pypi`

After registration, tagging a release publishes with no token — GitHub mints a
short-lived OIDC credential. (The bundled import modules stay `nx_*` — e.g. the
single `nx-ai-engineer` wheel ships `import nx_core`, `import nx_cli`, …)

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
   python scripts/bump_version.py 2.1.0
   python scripts/bump_version.py --check     # confirms every string agrees
   ```
3. **Update docs** — move the `[Unreleased]`/top notes into a dated
   `## [2.1.0]` section of `CHANGELOG.md`; refresh `RELEASE_NOTES.md` and
   `ROADMAP.md` if needed.
4. **Commit & tag** — the tag must equal the version (the workflow guards this):
   ```bash
   git commit -am "release: 2.1.0"
   git tag v2.1.0
   git push && git push --tags
   ```
5. **Automation takes over** (`release.yml` on the `v*` tag):
   - re-runs the Quality Gate (release is blocked if it fails),
   - verifies the tag matches the package version,
   - builds the single self-contained sdist + wheel (`twine check`),
   - publishes it to PyPI via **Trusted Publishing (OIDC)** — or the
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
- [ ] PyPI auth configured — **either** a trusted publisher for `nx-ai-engineer`
      (Option A) **or** the `PYPI_API_TOKEN` secret (Option B)
- [ ] Tag `v<version>` pushed → release workflow green → package on PyPI + GitHub Release

## Verifying a published release

```bash
pip install nx-ai-engineer==<version>
nxai version      # matches the tag
nxai doctor       # all packages aligned
```
