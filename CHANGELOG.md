# Changelog

All notable changes to NX AI Engineer are documented here. Format:
[Keep a Changelog]; versioning: [Semantic Versioning](https://semver.org).

## [1.0.0] — 2026-06-23 · first public platform release

**NX AI Engineer becomes a Developer Infrastructure Platform** — distributable via
PyPI, installable with a single `nxai` CLI, and prepared for long-term open-source
evolution. No engine behavior was removed; this release is about distribution,
packaging and the official product surface.

### Added
- **Engineering Packs** — a new `nx-packs` package shipping a catalog of **domain
  knowledge bundles** (policies, patterns, checklists, ADRs, templates, examples,
  context) for engineering domains. Two reference packs are authored in full
  (**lgpd**, **security**/OWASP) plus structured scaffolds for owasp, ai, cloud,
  docker, multi-tenant, observability, testing, billing, authentication. Managed
  via `nxai pack <list|show|add|remove>`; once installed under `.ai-project/packs/`,
  a new **Pack Provider** feeds the pack's policies/checklists/context to the
  agents working in that domain. Packs contain **no code and no AI** (enforced by
  the test suite). Third parties can publish their own packs (the Marketplace).
  New `PACKS_GUIDE.md`.
- **Repository standardization** — a `repo-standards` Engineering Pack plus a
  `nxai scaffold` command that lays open-source/GitHub standards into a project's
  repo root: governance files (CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/.editorconfig),
  `.github/` issue & PR templates, a stack-matched CI workflow (Python/Node/Go/
  generic) and `.gitignore`. Idempotent (never overwrites without `--force`),
  with `--stack auto` detecting the stack from the audit and `--dry-run` to preview.
- **CLI**: `nxai graph` (top-level Knowledge Graph), `nxai report` (consolidated
  status + insights + metrics), `nxai pack`, and `nxai scaffold`.
- **Open-source / ecosystem docs**: `PROVIDER_SDK_GUIDE.md` (author Knowledge
  Providers), `MARKETPLACE.md` (distribute third-party packs/plugins as PyPI
  packages), and a maintainer `RELEASING.md` (release process + publication
  checklist). New `scripts/bump_version.py` keeps the version in lock-step across
  all packages (`--check` verifies; `<version>` sets) — release automation that
  removes the version-duplication maintenance risk.
- **Official `nxai` CLI** with the full product surface, including new commands:
  `nxai init` (scaffold + audit + Brain + Knowledge + Vault), `nxai update`
  (refresh template assets only), `nxai doctor` (health-check install + project),
  `nxai docs` (read the bundled guides), `nxai execute` (full end-to-end flow) and
  `nxai version`. All 19 previous commands are preserved. The legacy `nx` console
  script remains as an alias.
- **PyPI distribution.** `pip install nx-ai-engineer` installs the 8 `nx-*`
  packages and the `nxai` script — **no manual file copying**. The deployable
  template (agent specs, doc/code templates, project rules, guides, config
  example) ships as **package data** inside `nx-cli` (`nx_cli/_template/`).
- **Data-only `.ai-project/`.** The platform code lives in the installed packages;
  a project's `.ai-project/` holds **only data** (config + Brain + Vault +
  Knowledge + tasks/locks/reviews/history). `nxai init` scaffolds it; `nxai update`
  refreshes template assets while **never** touching Brain/Vault/Knowledge/config/
  history.
- **Official Obsidian vault structure** — the numbered layout `00 Dashboard`,
  `01 Architecture`, `02 ADR`, `03 Decisions`, `04 Features`, `05 APIs`,
  `06 Services`, `07 Database`, `08 Workflows`, `09 Bugs`, `10 Lessons Learned`,
  `11 Roadmap`, `12 Releases`, `13 Metrics`, `14 Retrospectives` — created during
  `init` and auto-synced. Still a reflection of the Brain, never the source of
  truth; sync stays incremental.
- **Open-source infrastructure**: GitHub Actions CI (quality gate matrix + acyclic
  graph + wheel build/smoke), a tag-driven **release** workflow (PyPI publish +
  GitHub Release with a version/tag guard), issue & PR templates, and new
  **Installer** and **Upgrade** guides.

### Changed
- **Version reset to `1.0.0`** for the first public release of the platform
  (previously `5.0.0-rc1` during internal development).
- Product positioning: from "AI Engineering framework" to **Developer
  Infrastructure Platform** — *all intelligence belongs to the model; all
  organization belongs to NX*.
- The Quality Gate now requires the Installer and Upgrade guides and validates the
  six new CLI commands.

### Fixed
- **Architecture integrity (post-audit):** broke a real `nx-obsidian ↔ nx-knowledge`
  import cycle by relocating the `relate`/graph primitive (`KnowledgeGraph`,
  `KnowledgeGraphBuilder`) **down** into `nx-providers` (both layers depend on it
  downward; it fits the providers' "relate" role). Declared the previously
  undeclared `nx-cli → nx-sdk` edge.
- **Honest guardrails:** the Knowledge-doctrine test now scans the real
  `nx_knowledge/knowledge` layer and detects `nx_*` reasoning imports (it
  previously scanned a non-existent path and passed vacuously);
  `scripts/verify_packages.py` now also verifies the **real** (AST-scanned)
  cross-package import graph is acyclic and matches each package's declared
  `dependencies`, not just the declared graph.
- **Deployment cleanup (post-audit):** removed the repo-layout `sys.path`
  injection from every installed package `__init__` and the CLI (relied on
  ordinary package resolution — no more shadowing site-packages); `config_root()`
  now falls back to `<cwd>/.ai-project` instead of pointing into the install tree;
  pinned intra-workspace dependencies to `==1.0.0` and de-duplicated the console
  scripts to the `nx-cli` package; surfaced previously-silent failures as bus
  events (`lock.check_error`, `knowledge.unavailable/index_error/obsidian_error`,
  `evolution.error`); the Project Brain code-guard now recurses into nested
  list/dict values; `git()` gained a timeout; added `WorkflowRegistry.clear()`.
  Refreshed the user-facing docs/examples (`nxai`/`nx_*`, no broken paths),
  rewrote `RELEASE_NOTES` for 1.0.0, and moved point-in-time audit reports to
  `docs/history/`.

### Notes
- The Knowledge Engine doctrine is unchanged (five responsibilities, never
  reasons); the Project Brain still never stores code or model output.

---

## [Pre-1.0 development history]
### Added
- **Monorepo** (`packages/` + `pyproject.toml` + `LICENSE` + `.github/ci.yml` +
  `website/` + `installer/`): the platform is split into **8 acyclic packages**
  (nx-core, nx-workflow, nx-sdk, nx-providers, nx-obsidian, nx-knowledge,
  nx-runtime, nx-cli), each an **independently importable** package.
  `scripts/verify_packages.py` enforces the acyclic graph (CI);
  `test_nx_packages.py` covers the package imports.

### Changed
- **Monorepo physical relocation complete** (see `docs/MIGRATION_PLAN.md`): all
  source now lives under `packages/nx-*/`. Cross-package imports were rewritten to
  absolute `nx_*`; each layer's subdirectory structure is preserved inside its
  package so intra-package relative imports stay valid. The `knowledge` layer was
  split across nx-providers / nx-obsidian / nx-knowledge along acyclic edges (the
  composition-root `pipeline` and the all-aggregating `registry` were placed to
  avoid a package cycle). The Quality Gate scans the relocated code under
  `packages/` for cycles/unused-imports.
- **Test-suite** moved to top-level `tests/` (210 tests) and the **examples**
  rewritten to import `nx_*` directly.
- **Deployment** (`scripts/init_aies.py`) now installs both `framework/` and
  `packages/` into `<target>/.ai-project/`, and the deployed orchestrator shim
  locates `packages/` by walking up from itself — so the copy-based install keeps
  working after the split (verified end-to-end).

### Added
- **Static website generator** (`website/generate.py`, stdlib-only): renders the
  README/architecture/guides/ADRs and a per-package index into a static HTML site.

### Removed
- **`aies` compatibility shim** (SemVer-major cut-over): `framework/tools/aies/` is
  deleted; all imports use the `nx_*` packages. (`aies.*` no longer resolves.)
  Stays green throughout (**210 tests, no cycles, no unused imports, acyclic graph,
  stdlib-only**).
- **Project Knowledge Engine doctrine** (ADR-0018): the engine now exposes its
  **exactly five responsibilities** as named methods — `discover`, `index`,
  `relate`, `update`, `deliver_context` (`KnowledgeEngine.RESPONSIBILITIES`). It
  does NOT learn programming, improve models, or reason — all intelligence
  belongs to the model; it only reduces cognitive load. A guardrail test fails
  the build if the `knowledge` layer imports any reasoning layer. `knowledge
  status` shows **context richness** (richer history → fewer tokens). New doc
  `PROJECT_KNOWLEDGE.md`.
- **Knowledge Graph** (ADR-0017): the Knowledge Engine automatically builds a
  typed graph relating project elements (Service→API→DB→Migration→Test→ADR→Bug→
  Feature→Sprint→Doc→Obsidian), inferred from structured knowledge (never from
  code). Used **only to enrich** agent context (related APIs/tests/services/docs/
  ADRs/bugs) — never to replace the model's reasoning. New `knowledge graph
  [--format mermaid|json] [--query <path>]`; the Obsidian Relationships note
  renders the element graph.
- **Project Evolution** (ADR-0016): every agent execution now enriches structured
  project knowledge. The Project Evolution engine classifies changed file
  paths/metadata (never code) into Brain facets — modules, services, APIs,
  entities, tests, integrations, dependencies, patterns, fixed bugs, technical
  decisions, lessons learned and related files. **Never stores code or model
  responses.** New Brain facets `tests`/`integrations`/`dependencies`/`lessons`;
  `insights` reports the accrued counts.
- **Knowledge Providers** architecture (ADR-0013): no knowledge source is coupled
  directly to the Context Engine — everything flows through a `KnowledgeProvider`
  (Filesystem, Git, Markdown, ADR, Project-Brain, Obsidian) via a
  `KnowledgeRegistry`. New `knowledge` CLI command. Providers only index/catalog/
  retrieve/enrich/relate — never decide, interpret code, or generate answers.
- **Knowledge Engine** (ADR-0015): the single coordination + access point for the
  three project memories — **Project Brain** (operational), **Obsidian**
  (organizational) and **Git** (historical) — keeping them synchronized. Realizes
  the flow `Brain → Knowledge Engine → Providers → Obsidian → Context Engine →
  Agents`. New `knowledge sync [--commit]` / `knowledge status`; opt-in Git
  snapshot via `config.knowledge_git_snapshot`. The Context Engine now retrieves
  through the Knowledge Engine.
- **Obsidian visual knowledge vault** (ADR-0014): `ObsidianSync` projects the
  Project Brain into an auto-synced, incremental Obsidian vault — one note per
  category (ADRs, Architecture, Roadmap, Features, Services, APIs, Modules,
  Dependencies, Known Bugs, Decisions, Retrospectives, Lessons Learned), a
  navigation index, a Mermaid relationship map and ADR backlinks. Reflects the
  Brain (not a source of truth), never duplicates, syncs on
  `pipeline.completed`/`adr.created`. New `obsidian sync|status` CLI; config
  `obsidian_sync` / `obsidian_vault`.

### Changed
- Context Engine sources its file list from the Filesystem Provider (no direct
  `os.walk`) and enriches docs/patterns from the Markdown/ADR/Brain providers.
  Backward compatible (`ContextBuilder` API/outputs unchanged).

---

## [5.0.0-rc1] — 2026-06-22
First **Release Candidate** — stabilization, consistency and documentation. No
new product features; quality, DX and production-readiness.

### Added
- **Quality Gate** (`scripts/quality_gate.py`): tests, import-cycles,
  unused-imports, public-CLI, public-API and docs gates. A PR/release fails if
  any gate fails.
- **CLI test suite** (`test_cli.py`) covering all 17 commands + adapter resolution.
- Required documentation set: ROADMAP, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT,
  RELEASE_NOTES, MIGRATION_GUIDE, SDK_GUIDE, PLUGIN_GUIDE, ENGINE_GUIDE,
  WORKFLOW_GUIDE, PROJECT_BRAIN, ARCHITECTURE_OVERVIEW.
- `examples/` — 8 runnable examples (agent, engine, workflow, adapter, plugin,
  project integration, full pipeline, Project Brain update).

### Changed
- **Single source of truth** for the canonical agent order (`agents.CANON_ORDER`);
  the planner, dispatcher and execution scheduler now import it (was duplicated).
- Version bumped `1.0.0` → `5.0.0-rc1` (SemVer pre-release).

### Removed
- Dead code: `schedulers.execution.LockConflict` (unused).
- ~13 genuinely unused imports across the package.

### Fixed
- `test_compat` version regex accepts SemVer pre-release tags.

---

## [4.0.0] — Autonomous platform
- **Decision Engine** (ADR-0011): auto-decides agents/workflow/order/risk/impact/
  cost/time/Review/QA/parallelism.
- **Autonomous Learning** (ADR-0012): Self-Improvement, Experience Analyzer,
  Pattern Discovery, Similar-Task Detection, Recommendation, Knowledge Evolution,
  Brain Optimizer. The platform learns after each run (knowledge, never code).
- **Execution Cluster** (ADR-0010): worker pool, internal queue, scheduler,
  concurrency, priorities — over a shared `NodeExecutor`.
- **ClaudeCodeAdapter** (ADR-0009): real execution via the Claude Code CLI,
  mode-aware (Dry Run → Test → Execute), timeout/retry/cancel.
- Unified **Pipeline** (ADR-0006), **Governance + Delivery** (ADR-0005),
  **Observability/telemetry** (ADR-0007), **SDK** (ADR-0008).

## [3.0.0] — Memory
- **Context Engine** (ADR-0003), **Project Brain** (directory-based) + Learning +
  Experience + Semantic stub (ADR-0004).

## [2.0.0] — Execution
- **Execution Engine** + mandatory Dry Run → Test → Execute gate (ADR-0001).
- **Agent Dispatcher** with Strategy Pattern (ADR-0002).

## [1.0.0] — Foundation
- Audit, plan, locks, worktrees, review; 13 agents; generic, stdlib-only.
