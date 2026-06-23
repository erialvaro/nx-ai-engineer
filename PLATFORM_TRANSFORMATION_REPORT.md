# NX AI Engineer — Executive Report: Framework → Developer Infrastructure Platform

**Date:** 2026-06-23 · **Version:** 1.0.0 · **Status:** ready for GitHub + PyPI
**Quality:** 218 tests green · acyclic package graph · stdlib-only · `nxai init`
validated end-to-end.

This report documents the transformation of NX AI Engineer from a copy-based
framework into a distributable, installable, versioned **Developer Infrastructure
Platform**. No engine behavior was removed; the work concentrated on distribution,
packaging, the official product surface, and open-source readiness.

---

## 1. Mission & positioning

> **NX AI Engineer is a Developer Infrastructure Platform for AI-assisted
> development. It organizes knowledge, context and execution to potentiate any AI
> model. It does not replace Claude Code, GPT, Gemini or any model. All
> intelligence belongs to the model; all organization belongs to NX.**

The product is now installed (`pip install nx-ai-engineer`) and driven entirely
through the official **`nxai`** CLI — never through manual file copying.

---

## 2. Final architecture

### 2.1 Repository (monorepo)
```
packages/      8 acyclic, stdlib-only packages (the platform code)
docs/          repo/architecture docs (contributor + website)
examples/      runnable examples (nx_*)
tests/         218 tests (top-level, nx_*)
website/       stdlib-only static site generator
installer/     source-checkout installer (delegates to nxai init)
scripts/       quality_gate.py, verify_packages.py, init_aies.py (legacy shim)
.github/       CI (gate matrix + graph + wheel build) + tag-driven PyPI release
               + issue/PR templates
framework/     legacy source shim (tools/orchestrator.py) — repo-run fallback
README · CHANGELOG · ROADMAP · LICENSE · pyproject.toml (metapackage)
```

### 2.2 Packages (acyclic)
```
nx-core ← nx-workflow ← nx-sdk
nx-core ← nx-providers ← nx-obsidian ← nx-knowledge
{core, workflow, sdk, knowledge} ← nx-runtime ← nx-cli
```
| Package | Responsibility |
|---|---|
| `nx-core` | Kernel (domain/states/lifecycle/engine), governance, observability, foundation |
| `nx-workflow` | Reusable multi-step workflows |
| `nx-sdk` | Public extension surface (agents/engines/workflows/adapters/plugins/tools) |
| `nx-providers` | Knowledge providers (filesystem/git/markdown/adr/project-brain) |
| `nx-obsidian` | Obsidian provider + vault sync (00–14 structure) |
| `nx-knowledge` | Knowledge Engine, graph, registry, memory (Brain), evolution |
| `nx-runtime` | Adapters, schedulers, intelligence, engines, composition-root pipeline |
| `nx-cli` | Official `nxai` CLI **+ the deployable template** (`nx_cli/_template/`) |

### 2.3 Distribution model
- **Code** ships in the installed packages (site-packages).
- **Template** (agent specs, doc/code templates, project rules, guides, config
  example) ships as **package data** inside `nx-cli` (`nx_cli/_template/`).
- **`.ai-project/` is data-only**: `config.json` + Brain + Obsidian vault +
  knowledge + working state (tasks/locks/reviews/logs/memory). No code lives there.

### 2.4 The three memories (unchanged doctrine)
- **Operational** — Project Brain (`brain/`), structured knowledge, never code.
- **Organizational** — Obsidian vault, numbered `00 Dashboard` … `14
  Retrospectives`, auto-synced, a reflection of the Brain (not source of truth).
- **Historical** — Git snapshots (opt-in).

The **Knowledge Engine** keeps its five responsibilities (discover, index, relate,
update, deliver_context) and never reasons.

---

## 3. Modules reorganized (what moved & why)

| Change | From | To | Justification |
|---|---|---|---|
| Deployable template | `framework/{agents,templates,docs,…}` | `packages/nx-cli/nx_cli/_template/` | Must ship in a wheel so `pip install` + `nxai init` need no manual copy. |
| Doc source for gate/website | `framework/docs/` | `nx_cli/_template/docs/` | Single source; ships with the product; `nxai docs` reads it offline. |
| Bootstrap | `init_aies.py` copies framework+packages | `nx_cli/bootstrap.py` (`init`/`update`) | Data-only `.ai-project`; upgrades never touch user data. `init_aies.py` now delegates. |
| Obsidian vault | flat 12 categories | numbered `00 Dashboard`…`14 Retrospectives` | Official product structure; Modules/Dependencies folded into Architecture; added Database/Workflows/Releases/Metrics. |
| CLI entry | `nx` → `orchestrator.py` | **`nxai`** (+ `nx` alias) + 6 new commands | Official binary; `init/update/doctor/docs/version/execute` added, all 19 prior commands preserved. |
| Versioning | `5.0.0-rc1` | **`1.0.0`** | First public release of the platform. |

**Nothing was removed**: every prior CLI command, SDK function, engine and test
remains; new surface is additive.

---

## 4. Justifications (key decisions)

1. **Package-data template + data-only `.ai-project`** — the only model that makes
   `pip install` + safe upgrades work. Code is swapped via pip; knowledge is never
   at risk. (ADR-0019.)
2. **`nxai` as the single interface** — one stable, discoverable CLI; the legacy
   `nx` alias and source shims preserve every existing entry point.
3. **Numbered vault 00–14** — the requested official structure; preserves the
   ADR-0014 doctrine (reflects the Brain, incremental, no duplication).
4. **Reset to 1.0.0** — the platform is a new public product; SemVer starts clean.
5. **`framework/` kept as a thin source shim** — repo-run fallback without forcing
   an install during development; not part of the wheel.

---

## 5. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Wheel omits `_template` data | Low | `package-data` globs **+** `MANIFEST.in` + `include-package-data`; CI `build` job builds wheels and the release blocks if the gate fails. (Wheel build not runnable offline here — validated in CI.) |
| `nxai update` clobbers user customizations | Low | `update` only refreshes template-derived files; never touches `config.json` or any data dir (covered by `test_bootstrap`). |
| Vault structure change surprises existing users | Low | Old flat notes are pruned by the incremental manifest; doctrine preserved; documented in CHANGELOG + ADR-0014/0019. |
| Version drift across 8 packages | Low | `nxai doctor` checks alignment; single 1.0.0 across all `__init__` + pyprojects. |
| PyPI publishing of 9 dists | Medium | Release workflow builds all + `twine check`; `--skip-existing`; tag must equal version. Trusted publishing planned (1.1). |
| Docs still using legacy prose ("AIES") | Low (cosmetic) | Import examples swept to `nx_*`; product naming updated in README/SKILL/guides; deeper prose polish is a follow-up. |

---

## 6. Future improvements

- PyPI **trusted publishing** (per-package OIDC) instead of a shared token.
- `nxai init --template <preset>` and `nxai plugin <add|list>`.
- `nxai doctor --fix`; `pipx`/Homebrew install paths.
- Consolidate `framework/` shim away once installs are the norm.
- Website CI publish (GitHub Pages) from `website/generate.py`.

---

## 7. Publication checklist

- [x] Single CLI (`nxai`) — all interaction through it; no manual copy.
- [x] `pip install`-ready: metapackage + 8 packages with build-system; entry points.
- [x] Template ships as package data (`nx_cli/_template/`), validated by `nxai init`.
- [x] `nxai init` flow: scaffold → audit → Brain → Knowledge → Vault (e2e verified).
- [x] `nxai update` refreshes template only; preserves Brain/Vault/config/history.
- [x] Obsidian vault `00 Dashboard` … `14 Retrospectives` created on init.
- [x] SemVer 1.0.0 across all packages; `nxai version` / `doctor` aligned.
- [x] `.github/` CI (gate matrix + graph + wheel build) + tag-driven PyPI release.
- [x] Issue/PR templates; Installer + Upgrade guides; ADR-0019.
- [x] README/CHANGELOG/ROADMAP/SKILL updated to the platform + `nxai`.
- [x] Quality Gate green (218 tests, no cycles, no unused imports, CLI/API, docs).
- [x] Acyclic package graph (`verify_packages.py`).
- [ ] Build wheels in CI and `twine upload` (runs on first `v1.0.0` tag).
- [ ] Create the GitHub repository and push; configure `PYPI_API_TOKEN` secret.

**To publish:** create the GitHub repo, set the `PYPI_API_TOKEN` secret, then
`git tag v1.0.0 && git push --tags` — the release workflow builds, verifies,
publishes to PyPI and cuts the GitHub Release.
