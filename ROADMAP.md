# NX AI Engineer Roadmap

Direction for the platform. Items are intentionally additive — the core (Kernel,
Engine contract, SDK) should not need structural refactoring.

## 1.0.0 (current — first public platform release)
- ✅ Developer Infrastructure Platform: PyPI distribution, official `nxai` CLI,
  data-only `.ai-project-assistant`, package-data template, `init`/`update`/`doctor`/`docs`.
- ✅ Obsidian vault official numbered structure (`00 Dashboard` … `14 Retrospectives`).
- ✅ Open-source infra: CI matrix + wheel build, tag-driven PyPI release, issue/PR
  templates, Installer/Upgrade guides.

## 1.1 — Distribution polish
- Publish to PyPI under trusted publishing (per-package OIDC).
- `nxai init --template <name>` (project-type presets) and `nxai plugin <add|list>`.
- Homebrew/pipx install docs; `nxai doctor --fix` for common issues.

## Post-1.0 — Real execution hardening (was 5.1)
- `ClaudeCodeAdapter`: real `test` sandbox (read-only permission mode) and robust
  `changed_files` via pre/post diff.
- Run **resume** from persisted `runs/<id>.json` for the Execution Cluster.
- Worker-utilization metrics into Experience/telemetry.

## Later — Smarter intelligence
- Decision Engine consults the Recommendation Engine (close the learning loop:
  decide using what was learned).
- Pipeline auto-sizes `--workers` from `decision.parallelism`.
- Per-file locks + write-time scope enforcement (hook).

## Later — Semantic memory
- Real vector `SemanticIndex` (embeddings) registered via the SDK; better
  Similar-Task Detection and recommendations.

## 2.0 — Ecosystem
- Plugin distribution/discovery convention (still explicit, never auto-remote).
- Additional first-party adapters (other models/CLIs).
- Optional parallel multi-run orchestration.

## Non-goals
- Third-party runtime dependencies in the core (stays stdlib-only).
- Mutating product code without an explicit adapter (Dry Run stays default).
- Storing source code in the Project Brain (knowledge only, always).
