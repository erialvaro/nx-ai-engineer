# Monorepo Migration Plan — nx-ai-engineer

Target layout (the structure you proposed), with **corrected, acyclic package
boundaries**. The working implementation currently lives in
`framework/tools/aies/` and is migrated **package-by-package, verified by the
Quality Gate at each step** (never a one-shot big-bang — a half-migrated tree is
worse than none).

```
nx-ai-engineer/
  packages/  nx-core nx-runtime nx-cli nx-sdk nx-providers nx-knowledge nx-obsidian nx-workflow
  docs/  examples/  templates/  tests/  website/  installer/  scripts/  .github/
  CHANGELOG.md  ROADMAP.md  LICENSE  README.md  pyproject.toml
```

## ⚠️ Findings that corrected the boundaries

### Finding 1 — the naive split creates a PACKAGE CYCLE
`kernel/pipeline.py` is the composition root (imports everything) and
`intelligence → schedulers`. Putting `kernel` in **nx-core** and `schedulers` in
**nx-runtime** yields `nx-core → nx-runtime` (pipeline/intelligence) **and**
`nx-runtime → nx-core` (schedulers→kernel) = **cycle**, violating the project's
zero-cycles invariant.
**Resolution:** the **composition root (`pipeline`) moves to nx-runtime**, not
nx-core. nx-core holds only pure primitives.

### Finding 2 — the `knowledge/` layer must be split across 3 packages
`nx-providers` / `nx-obsidian` / `nx-knowledge` slice one cohesive layer whose
internal imports are relative (`engine → registry/obsidian_sync`). The split
turns those into cross-package imports, so the move must rewrite them.
**Resolution:** split along the acyclic edges below; `engine`/`graph` depend on
`providers` and `obsidian`, never the reverse.

## Package map (acyclic — verified by `scripts/verify_packages.py`)

| Package (`nx_*`) | Moved layers | Depends on |
|------------------|--------------|------------|
| **nx-core** | util, config, agents, kernel/{domain,states,lifecycle,engine}, governance, observability, experience | — |
| **nx-workflow** | workflow | core |
| **nx-sdk** | sdk | core, workflow |
| **nx-providers** | knowledge/{base,filesystem,git,markdown,adr,project_brain,registry} | core |
| **nx-obsidian** | knowledge/{obsidian,obsidian_sync} | core, providers |
| **nx-knowledge** | knowledge/{engine,graph}, memory, evolution | core, providers, obsidian |
| **nx-runtime** | adapters, schedulers, intelligence, engines, **kernel/pipeline** | core, workflow, sdk, knowledge |
| **nx-cli** | orchestrator | all |

Dependency edges (all point down — **no cycles**):
```
nx-core ← nx-workflow ← nx-sdk
nx-core ← nx-providers ← nx-obsidian ← nx-knowledge
{core,workflow,sdk,knowledge} ← nx-runtime ← nx-cli
```

## Strategy: strangler-fig (facades first, relocate behind them)

A pure big-bang (move 78 modules + rewrite every import + split `knowledge/` in
one shot) cannot be landed *green* reliably in one pass — a half-migrated tree is
worse than none. So the migration is **inverted to be safe**: the `nx_*` packages
become real, importable facades **first** (zero risk, build stays green), and the
source is **relocated behind them** as the final mechanical step.

### Stage 1 — facades (DONE, verified green)
Each `packages/<pkg>/<nx_mod>/__init__.py` installs a **meta-path finder** that
maps `nx_*.<sub>` to the corresponding `aies.*` module — importing it under its
**real (aies) name** so relative imports resolve correctly, then exposing it as
`nx_*`. Result:
- all 8 packages import independently (`import nx_core`, `from nx_knowledge.engine
  import KnowledgeEngine`, `from nx_runtime.pipeline import Pipeline`, …);
- the objects are **identical** to `aies.*` (no duplication) — `Node is
  aies.kernel.domain.Node`;
- the package dependency graph is **acyclic** (`scripts/verify_packages.py`);
- the Quality Gate stays green (now **208 tests**, incl. `test_nx_packages.py`).

### Stage 2 — physical relocation (DONE — all 8 packages relocated, gate green)

All source physically lives under `packages/`; `framework/tools/aies/` is now just
the compatibility shim (`__init__.py` = reverse finder) plus the test-suite. Each
move kept the Quality Gate green — **208 tests, no cycles, no unused imports**.

| Package | Status | Notes |
|---------|--------|-------|
| **nx-core** | ✅ **relocated** | foundation, kernel/{domain,states,lifecycle,engine}, governance, observability, experience + flat modules. Self-contained → no cross-import rewrite. |
| **nx-workflow** | ✅ **relocated** | rewrote `..kernel.engine` → `nx_core.kernel.engine`. |
| **nx-sdk** | ✅ **relocated** | rewrote `..workflow.workflow` → `nx_workflow.workflow`. |
| **nx-providers** | ✅ **relocated** | knowledge/{base,filesystem,git,markdown,adr,project_brain} → import core via `nx_core.*`; intra-layer `.base` kept relative. |
| **nx-obsidian** | ✅ **relocated** | knowledge/{obsidian,obsidian_sync}; `.base`/`.adr` → `nx_providers.*`, `..foundation` → `nx_core.*`. |
| **nx-knowledge** | ✅ **relocated** | knowledge/{engine,graph,**registry**}, memory, evolution. registry/obsidian refs → `nx_providers.*`/`nx_obsidian.*`. The `knowledge/__init__` re-assembles the split layer's public API. |
| **nx-runtime** | ✅ **relocated** | adapters, schedulers, intelligence, engines, **kernel/pipeline** (composition root). pipeline rewires to `nx_core.*`/`nx_knowledge.*`/`nx_sdk`. |
| **nx-cli** | ✅ **relocated** | orchestrator → `nx_core.*` / `nx_runtime.*` / `nx_sdk`; thin shim left at `framework/tools/orchestrator.py`. |

The layer **subdirectory structure is preserved inside each package** (e.g.
`nx_knowledge/knowledge/`, `nx_runtime/kernel/`) so intra-package relative imports
stay valid; only imports that cross a package boundary were rewritten to absolute
`nx_*`. The `aies.*` surface is preserved by the reverse finder for the test-suite.

**Boundary correction (found during Stage 2):** `knowledge/registry.py` imports the
**Obsidian** provider (it aggregates *all* providers), so it cannot live below
obsidian. **`registry` moves to nx-knowledge**, not nx-providers (nx-knowledge
already depends on both providers and obsidian → still acyclic). The remaining
providers (base/filesystem/git/markdown/adr/project_brain) stay in nx-providers.

### Mechanism (proven on core + workflow)
Each package move: (1) physically move its files; (2) rewrite imports that cross
into another package to absolute `nx_*`; (3) drop that package's keys from the
forward finder (it becomes path-resolved/real); (4) add `aies.<layer> →
nx_<pkg>` to the `aies` reverse finder so layers still in `aies` keep working;
(5) run the Quality Gate. The relative imports **inside** a package are preserved,
and `import`-identity is kept (`Node is aies.kernel.domain.Node`).

### Original Stage 2 plan (reference)
Behind the stable facades, move each layer's source from `framework/tools/aies/`
into `packages/<pkg>/<nx_mod>/` in dependency order (core → workflow/sdk →
providers → obsidian → knowledge → runtime → cli), rewriting the now-cross-package
imports, and flip each facade entry from `aies.*` to the local module. Because
consumers already import `nx_*` (via the finder), each layer can be moved and
verified independently. When a package is fully physical, drop its finder entries;
when all are done, remove `aies` (SemVer major) and point the skill at `nx_cli`.

### Stage 3 — consolidate (DONE)
- ✅ **`aies` shim removed** (the SemVer-major cut-over). All source imports use
  `nx_*`; the `framework/tools/aies/` shim is deleted. The Quality Gate now scans
  only `packages/nx-*` for import-cycles/unused-imports; `verify_packages.py`
  enforces the acyclic graph.
- ✅ **Test-suite relocated** to top-level `tests/` (210 tests) and rewritten to
  import `nx_*`; `tests/__init__.py` bootstraps the package paths.
- ✅ **Examples** rewritten to `nx_*` (`examples/_bootstrap.py` points at
  `packages/`); all 8 examples run.
- ✅ **Website generator wired** — `website/generate.py` (stdlib-only) renders the
  docs/ADRs/per-package index into a static site; covered by `tests/test_website.py`.
- ✅ **Deployment fixed (critical).** `scripts/init_aies.py` now copies **both**
  `framework/` and `packages/` into `<target>/.ai-project-assistant/`, and the deployed
  `tools/orchestrator.py` shim locates `packages/` by walking up from itself — so
  `python .ai-project-assistant/tools/orchestrator.py <cmd>` works post-migration (verified
  end-to-end: audit, full pipeline dry-run, knowledge, status).

#### Why `framework/` is NOT flattened into top-level `docs/`+`templates/`
The repo has a deliberate **two-tier** layout, not an inconsistency:
- **Top level** (`packages/ docs/ examples/ tests/ website/ scripts/ installer/`)
  is the **monorepo** — for contributors, CI and publishing.
- **`framework/`** is the **deployable template** that `init_aies.py` copies into a
  consumer project's `.ai-project-assistant/` (agents, in-project docs, config, the
  orchestrator shim). Its `docs/`+`templates/` are the *end-user's* in-project
  reference material — distinct from the repo's contributor `docs/`.
Flattening `framework/docs`+`framework/templates` to the top level would conflate
those two audiences and break the copy-based deployment, so they stay in
`framework/`.

## Tooling
- `scripts/verify_packages.py` — asserts the package dependency graph is acyclic
  and matches this plan (wired into CI). **Passing.**
- The facade generator + finder live in each `packages/<pkg>/<nx_mod>/__init__.py`.

## Guarantees
- The Quality Gate (208 tests, no cycles, no unused imports) stays green at every
  step; a package's physical move is kept only if its step is green.
- No third-party dependencies are introduced (stdlib-only stays).
- Backward compatibility: `aies.*` keeps working until the major bump; `nx_*`
  works now.
