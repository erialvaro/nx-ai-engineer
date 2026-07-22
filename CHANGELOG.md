# Changelog

All notable changes to NX AI Engineer are documented here. Format:
[Keep a Changelog]; versioning: [Semantic Versioning](https://semver.org).

## [2.9.0] — 2026-07-22 · Visual QA + Responsive developer (browser-driven QA)

### Added
- **Two specialist agents — `responsive` (developer) and `visual-qa` (QA).**
  Give the AI eyes on a real browser and collapse the *change → open browser →
  eyeball → fix* loop.
  - **`responsive`** — the mobile-first WEB developer. Builds base→`sm`→`md`→`lg`,
    guarantees no horizontal overflow / clipped controls, fluid type, touch
    targets ≥ 44px, safe areas, sized media (no CLS). Runs right after `frontend`,
    owns responsive-dedicated files + Storybook stories + layouts, and receives a
    matched design reference. Hands off to `visual-qa`.
  - **`visual-qa`** — drives the running app with **Playwright** across the device
    matrix (360×640, 390×844, 768×1024, 1024×768, 1366×768, 1920×1080 + iPhone
    SE/15/16, Pixel 9, Galaxy S24, iPad), gating horizontal overflow, clipped
    elements, contrast + WCAG 2.2 AA, CLS/LCP and **Lighthouse ≥ 95**, and
    pixel-diffing baselines (**BackstopJS**). Owns the visual-test infra (more
    specific than `qa`, so routing prefers it); reports defects with before/after
    screenshots and hands the fix to the owning developer. Runs after `qa`,
    before `reviewer`.
- **`visual-qa` Engineering Pack** — the browser-driven QA doctrine: `workflow.md`
  (the closed loop), `device-matrix.md`, `responsive.md`, `accessibility.md`
  (WCAG 2.2 AA), `performance.md` (Core Web Vitals + the Lighthouse gate),
  `tooling.md` (Playwright, Playwright MCP, BrowserTools MCP, Lighthouse CI,
  BackstopJS, Storybook, React DevTools, Tailwind IntelliSense, ESLint, Prettier,
  Android Studio / Genymotion, Chrome DevTools), `anti-patterns.md`, a specialist
  prompt and a before/after report template. Attaches to `visual-qa`, `responsive`,
  `frontend`, `mobile` and `qa`; `design-references` now also feeds `responsive`.
- **Scaffold ships the loop.** `nxai new` (cloud-agnostic) generates
  `frontend/playwright.config.ts` (device matrix), a responsive + a11y spec,
  `backstop.json`, `lighthouserc.json` (assertions at 0.95), a Storybook setup,
  npm scripts (`test:visual`, `test:regression`, `lhci`, `storybook`), a `make
  visual` target and a `visual-qa` CI workflow.

## [2.8.0] — 2026-07-19 · Free-port preflight before bringing a project up

### Added
- **`nxai port` command + `nx_core.net` primitive.** Before a project is brought
  up on `http://localhost`, the wanted port may already be taken (a stale
  container, another dev server) — startup then fails. `nxai port [preferred]`
  probes the preferred port and scans upward for the first **bindable** one,
  printing where to bring the app up (`--host`/`--span` tune the probe; `-q`
  prints only the number so scripts can do `PORT=$(nxai port 8000 -q)`).
  - **`nx_core.net`** — stdlib-only helpers `is_port_free(port, host)` and
    `find_free_port(preferred, host, span=…)` (pure `socket`, no third-party
    dep). Re-exported from `nx_core.foundation`.
  - **Scaffold preflight** — the `cloud-agnostic` stack ships
    `scripts/check-ports.py` and runs it (advisory, non-blocking) in `make up`,
    plus a standalone `make ports` target, so generated projects verify
    `BACKEND_PORT`/`FRONTEND_PORT` are free and suggest a free alternative.
  - CLI grows to **26 commands**.

## [2.7.1] — 2026-07-19 · Design reference: Hostinger (web-hosting)

### Added
- **`hostinger` design reference** (`design-references` pack) — the library's first
  **web-hosting** vertical, distilled from https://www.hostinger.com/br/. Ships the
  signature Hostinger purple (`#673de6`) on white with a deep meteorite-violet dark
  theme (`#0a0a2c` / `#1b1145`), a DM Sans single-family type system, and the
  conversion-first hosting layout (pricing tiers, discount/percent-off badges,
  uptime stats, social-proof strip). Rich EN + PT-BR `industry`/`keywords`
  (hospedagem, domínio, vps, cloud, wordpress…) so the deterministic matcher selects
  it for hosting prompts. Data-only addition — no code change; the matcher reads the
  directory. Library grows to **15 profiles**.

## [2.7.0] — 2026-07-19 · Mobile specialist + design-reference library growth

### Added
- **`mobile` specialist agent + `mobile` Engineering Pack (React Native + Expo).**
  A native iOS/Android developer that executes against a full mobile standard —
  **architecture** (managed Expo, New Architecture, TypeScript), **typed
  navigation** (expo-router/react-navigation), **state & data** (TanStack Query,
  offline-first, `expo-secure-store`), **native modules & permissions** (Expo
  modules, in-context requests), **performance** (FlatList/FlashList, Reanimated on
  the UI thread, `expo-image`, Hermes), **EAS build/update/submit** + store
  readiness, and **mobile accessibility** (44pt targets, labels, reduce-motion,
  safe areas).
  - Slots into `CANON_ORDER` **after `frontend`**; owns RN/Expo-specific files
    (`App.*`, `app.json`/`app.config.*`, `eas.json`, `metro.config.*`,
    `**/*.native.*`, `screens/`, `navigation/`, `mobile/`, `expo/`) and is
    forbidden web/server/db paths. Routing prefers it for native config
    (`eas.json` → `mobile`).
  - **`design-references` now also feeds `mobile`** — palette/type/mood profiles
    are platform-agnostic, injected into the mobile theme (NativeWind), light +
    dark. *Adapt, never clone.*
  - Prototyping via the **`mockup-app-skill`** (referenced as tooling) to sketch
    screens/flow before wiring real data. Ships `prompts/specialist.md`, a
    `templates/screen-spec.md`, and the `agents/mobile.md` contract.
- **Design Reference Library grew to 14 profiles** (+8) — extracted from real
  sites, broadening the verticals the matcher covers:
  - `sweetags` (design-agency), `myfots` (fashion, minimal/mono), `petala-beauty`
    (cosmetics), `vicshop` (fashion, minimalist), `fwr-agencia` (digital-agency),
    `liloca` (fashion, playful), `tapetes-sao-jose` (home-decor), `lp-max-suzuki`
    (car-dealership landing page). Same-vertical entries are separated by `mood`
    (e.g. `moda minimalista` → myfots vs `moda divertida` → liloca).

## [2.6.0] — 2026-07-19 · Design Reference Library

### Added
- **`design-references` Engineering Pack + a deterministic reference matcher.**
  A library of **design-reference profiles** distilled from real, shipped sites —
  each declaring a **palette (light + dark tokens), a type pairing, a layout
  concept, mood and vertical** as structured data (`references/*.json`, validated
  by `references/schema.json`). When a `designer`/`frontend` Engineering Contract
  is built, NX matches the task prompt to the best-fit reference and injects it, so
  the agent generates UI **grounded in a concrete visual language** instead of
  inventing tokens — *adapt, never clone* (all `design`-pack gates still bind).
  - **Matcher** (`nx_providers.knowledge.design_refs`) — a knowledge-source
    primitive. Pure **deterministic tag overlap** (`vertical` ×3,
    `industry`/`mood`/`keywords` ×2), accent-folded (`salão`→`salao`), ties broken
    by `id`. No embeddings, no model, no network — matching the doctrine *packs
    organize data; the model reasons*. `mood` disambiguates same-vertical entries
    (`salão elegante` → Espaço Ellen Souza; `salão de luxo` → Odara Li).
  - **Contract surface** — `EngineeringContract.design_reference` (rendered in
    `to_text()`/`as_dict()`); populated only for `designer`/`frontend` when the
    pack is installed and a reference actually fits the prompt (else `None`).
  - **CLI** — `nxai design ref list | show <id> | match "<prompt>"` (reads the
    installed pack, falls back to the built-in seeds).
  - **Seed library (6)** — `hs-motors` (automotive, bold red/near-black,
    Clash Display + Satoshi), `espaco-ellen-souza` (beauty, elegant rose/gold,
    Playfair Display + Jost), `luque-construcoes` (construction, industrial
    orange, Archivo + Inter), `atelie-simone` (stationery, playful pinks,
    Pacifico + Nunito), `odara-li` (beauty, luxury gold, Fraunces + Inter),
    `pousada-luz-do-sol` (hospitality, coastal terracotta/teal, Fraunces +
    Plus Jakarta Sans).
  - Extend by dropping a schema-conforming `references/<id>.json` into the pack —
    no code change; third-party reference packs work the same way.

## [2.4.0] — 2026-07-13 · Designer (UI/UX) specialist

### Added
- **`designer` specialist agent + `design` Engineering Pack** (two-layer pattern).
  Designs interfaces **and** the system behind them, and hands the `frontend` agent
  a spec it can implement without guessing. Slots into `CANON_ORDER` **before
  `frontend`** (design informs implementation).
  - **Design system** — tokens (color, type, spacing, radius, shadow, z, motion) as
    the **single source of truth** (CSS vars → Tailwind → shadcn `components.json`),
    **light *and* dark**; no magic values in components.
  - **Typography / color / layout** — type scale + pairing, palette with roles,
    spacing scale, grid, mobile-first responsive.
  - **Accessibility (WCAG 2.2) as a release gate** — contrast verified in both
    themes, keyboard reachable, visible focus, semantic + labelled, target ≥ 24px,
    `prefers-reduced-motion`.
  - **Motion system** — duration + easing scale with **framer-motion**;
    transform/opacity only; never blocking; reduced-motion-safe.
  - **Mandatory states** — loading/skeleton, empty, error (not just the happy path).
  - **Performance-aware** — no CLS from unsized media, light LCP; the **`seo` pack
    now also feeds `designer`** (design decisions move Core Web Vitals).
  - **Tooling baked in** — `ui-ux-pro-max` (plan/review), the **21st.dev** family
    (`21st-cli-use` to reuse, `21st-ai` to generate, `21st-registry` /
    `21st-design-sync` to publish), **`dataviz`** (read before any chart), and
    shadcn/Tailwind as the default stack.
  Grouped under a new **`design`** category (`nxai pack add design`).

## [2.3.1] — 2026-07-13 · index ADRs in brain/decisions + surface Brain docs

### Fixed
- **ADRs placed in `brain/decisions/` are now indexed.** The ADR provider scanned
  `brain/adr/` but not `brain/decisions/` — yet `decisions` is also a Brain facet
  name, so an ADR-`*.md` dropped there was silently ignored. Added
  `brain/decisions/` to the scanned roots (only `ADR-*.md` matches, so no false
  hits). `nxai` still writes its own ADRs to `brain/adr/`; this just also honors
  the intuitive folder. (Note: `nxai init` does not create `brain/decisions/`;
  facet dirs are created on write.)

### Added
- **Free-form Brain markdown docs are now retrievable.** Briefs, requirements and
  context notes dropped under `.ai-project-assistant/brain/**/*.md` are surfaced by
  the Project Brain provider (kind `brain-doc`) — so they appear in
  `nxai knowledge list/retrieve`, even though the generic markdown/filesystem
  providers intentionally skip the AI's data home. ADRs remain the ADR provider's job.

## [2.3.0] — 2026-07-13 · ambient auto-recording (on by default)

### Added
- **`auto_record` — on by default.** From the moment `.ai-project-assistant` exists
  at the project root, knowledge-producing commands (`plan`, `execute`/`pipeline`,
  `run` in execute mode, `deliver`) **automatically persist to the Project Brain
  and sync the vault** — recording is ambient and never needs an explicit
  `nxai knowledge sync`. `nxai plan` also records the goal + acceptance criteria +
  risks to the Brain, so a project's requirements/decisions accrue as you work.
  Best-effort: recording can never break the command; disable with
  `"auto_record": false` in `config.json`. `PROJECT_RULES.md` updated to say so.

## [2.2.2] — 2026-07-13 · skip modern edge/build output dirs

### Fixed
- File-based knowledge providers and the project analyzer now skip modern JS/edge
  **build outputs** — `.open-next`, `.wrangler`, `.vercel`, `.turbo`,
  `.svelte-kit`, `.output`, `.astro`, `.parcel-cache`, `.angular` — which can hold
  thousands of generated files and bloated the filesystem index (e.g. `.open-next`
  alone added ~1.4k entries on a Cloudflare/OpenNext project). Added to `SKIP_DIRS`
  (`base.py`) and the analyzer's skip set; regression test added.

## [2.2.1] — 2026-07-13 · fix: knowledge sync hang + AI starts from project memory

### Fixed
- **`nxai knowledge` (sync/list/index) could hang** (and surface 0 items, even for
  the framework's own ADRs). Root cause: `config_root()` searched **up from the
  install location**, so a stray `.ai-project-assistant` in a parent (e.g. the
  user's home directory) hijacked project resolution to an unrelated, huge tree —
  which the **unbounded** Obsidian vault detection then walked ~forever. Now
  `config_root()` resolves from the **current project** (cwd / explicit start),
  never the install location, and the vault scan is **bounded**. Result:
  `knowledge index/list/sync` runs in ~1–2s and surfaces filesystem, git, ADRs and
  all three memories. Regression tests added.

### Changed
- `PROJECT_RULES.md` (laid down by `nxai init`) now instructs the AI to **start
  from the project's memory** (Project Brain / ADRs / knowledge / git history) and
  to **record decisions** via ADRs + `nxai knowledge sync` — additive snapshots
  that never rewrite the project's own Git history.

## [2.2.0] — 2026-07-13 · Copywriter specialist (tech & innovation, SEO-optimized)

### Added
- **`copywriter` specialist agent + `copywriter` Engineering Pack** (two-layer
  pattern: agent executes, pack holds the knowledge). Writes professional,
  **human-sounding** copy for **technology & innovation** audiences, **optimized
  for SEO**:
  - **Human voice** — a full `anti-patterns.md` screen of AI tells & clichés to
    avoid (throat-clearing openings, "delve/leverage/seamless", listicle tics,
    hedging boilerplate), plus `voice-and-tone.md` (varied rhythm, active voice,
    concrete specifics, a real point of view).
  - **Tech fluency** — `tech-domain.md` maps the tech universe (AI/LLMs, cloud,
    SaaS, devtools, startups, security) with a "precision over hype, never
    fabricate specs/numbers" rule.
  - **Persuasion** — `frameworks.md` (AIDA / PAS / BAB / FAB, headlines, CTAs).
  - **SEO writing** — `seo-writing.md` (search intent, answer-first, title +
    meta, internal links) that **pairs with the `seo` pack** — whose `applies_to`
    now also feeds the copywriter, so the agent gets both standards. Ships a copy
    brief template and a quality gate.
  Grouped under a new **`content`** category; slots into `CANON_ORDER` after `seo`.

## [2.1.1] — 2026-07-13 · SEO reports via PageSpeed Insights

### Changed
- The `seo` agent now generates SEO reports from **PageSpeed Insights**
  (<https://pagespeed.web.dev/> / the PSI API), analyzing **Mobile + Desktop**, as
  a **topic-by-topic** improvements report that mirrors the tool's output:
  Core Web Vitals → Performance → Opportunities → Diagnostics → Accessibility →
  Best Practices → SEO — each item **Finding → Impact → Fix**, closing with a
  prioritized action list. Adds `templates/report.md` to the `seo` pack (v1.1.0);
  `performance.md`/`checklists.md`/the agent spec name PSI as the canonical
  measurement tool.

## [2.1.0] — 2026-07-13 · SEO & AI-discoverability specialist

### Added
- **`seo` specialist agent + `seo` Engineering Pack** (the two-layer pattern:
  the agent executes, the pack holds the knowledge). It makes web apps/sites
  standards-compliant across the whole SEO surface **and** discoverable by AI
  answer engines:
  - **Crawlability/indexability** — `robots.txt` (never blocking CSS/JS),
    one self-referential canonical, correct status codes, XML sitemaps.
  - **Rendering for bots** — SSR/SSG/ISR so primary content is in the server HTML.
  - **On-page** — unique title/meta, single H1, semantic HTML, Open Graph/Twitter.
  - **Structured data** — valid schema.org **JSON-LD** matching visible content.
  - **Core Web Vitals** — LCP<2.5s / INP<200ms / CLS<0.1 budgets as release gates.
  - **Internationalization** — reciprocal `hreflang` + `x-default`.
  - **AI/LLM discoverability (GEO)** — `llms.txt`, answer-first structured content,
    E-E-A-T, entity clarity (`sameAs`), and a **deliberate AI-crawler policy**
    (GPTBot / ClaudeBot / PerplexityBot / Google-Extended).
  The pack auto-attaches to the `seo` / `frontend` / `docs` agents via
  `applies_to`; `nxai pack list` groups it under a new **`seo`** category. The
  agent slots into `CANON_ORDER` right after `frontend`.

## [2.0.1] — 2026-06-24 · full-audit remediation

A complete audit of the framework (architecture, security, code quality,
scaffolding output, tests, docs) drove this hardening release. No breaking
changes; 250 tests green.

### Security
- **Path traversal in `nxai new`** — `new_project()` now validates the project
  name (rejects path separators, `..`, absolute paths and drive letters) and
  asserts the resolved directory stays under the target parent, so a crafted
  name can no longer write files outside the intended folder.

### Fixed
- **SDK extension point was dead** — `pipeline.py` imported `from nx_sdk import
  sdk` (nonexistent); the `ImportError` was swallowed, silently dropping every
  `nx_sdk.on(...)` handler. Now `import nx_sdk as sdk`.
- **Destructive-SQL guard precedence** — `policies.py` parenthesizes
  `drop table` / `delete from … where` so the `where` guard applies correctly.
- **`nxai doctor`** now checks `nx_packs` (was omitted from the import/version set).
- **Atomic state writes** — `util.write_json` writes a temp file then
  `os.replace`, so a crash or concurrent reader never sees a half-written file.
- Engine robustness: cycle guard in the decision layering (no `RecursionError`),
  unique node ids for duplicate-agent subtasks (+ skip `None` agents),
  `RETRYING → BLOCKED` is now a legal transition (clean deadlock surfacing),
  collision-proof Brain record ids, surfaced (not swallowed) Brain-trim errors,
  Windows-path normalization in evolution stats, resolved Obsidian wikilink graph
  edges, pytest `test_*.py` recognized by the review "without tests" check, and a
  hardened cancel path in the Claude Code adapter.

### Generated foundation (`nxai new`)
- `make migrate` now also applies `supabase/policies.sql` + `seed.sql` (RLS tables
  were left locked before).
- Backend ships **env-driven CORS** and **fails closed** if `SECRET_KEY` is a
  default in production; `platform-audit` gained a CORS check.
- `NEXT_PUBLIC_API_URL` is passed as a **build arg** (it is baked at build time),
  so the prod image points at the right API.
- `wait-for.sh` uses a portable Python TCP probe (the `/dev/tcp` form failed under
  `sh`/dash); frontend gains ESLint config + a `test` script.

### Docs
- Corrected the README header (v2.0.1 · 250 tests), reframed `RELEASE_NOTES` /
  `ROADMAP` for 2.x, fixed the "8 → 9 packages" drift, removed dead
  `[tool.nx.workspace]` config, and hardened the CLI quality gate to count only
  top-level subcommands.

## [2.0.0] — 2026-06-24 · NX AI Engineer v2 — the Scaffolding Framework

**NX AI Engineer becomes a scaffolding framework.** Beyond a library you add to a
project, it now *creates* the project: one command lays down a complete,
Cloud-Agnostic production foundation — the `create-next-app` / `django-admin
startproject` moment for AI-native platforms. This is a product milestone (v2);
the change is **additive** — every existing command is unchanged, no breaking API.

### Added
- **`nxai new <project>`** — scaffold a runs-anywhere foundation from a stack
  template: FastAPI backend (Twelve-Factor, structured JSON logs, request-id
  correlation, a **decoupled Supabase adapter** swappable to plain PostgreSQL via
  one env flag), Next.js frontend (standalone output), Docker Compose (portable
  base + dev override + prod), Dockerfiles (multi-stage, non-root, health-checked),
  Makefile (`up/down/logs/build/shell/migrate/lint/test/clean`), `.env.example`,
  `environments/`, `scripts/`, `configs/`, `supabase/` (migrations + RLS policies +
  seed) and docs/ADRs. Then makes the project AI-ready via `.ai-project-assistant`.
  **No business logic — only the foundation.**
- **`nxai platform-audit`** — static production-readiness audit across **eight
  dimensions** (Cloud-Agnostic · Twelve-Factor · Docker · Security · Scalability ·
  Observability · Multi-Environment · Production-Ready), PASS/WARN/FAIL per check;
  `--strict` fails on warnings (CI). A freshly generated foundation scores green
  (25 checks, 0 failures).
- **Scaffolding engine** in `nx_cli.bootstrap`: `{{ variable }}` rendering + a
  `dot.` → dotfile convention + a pluggable `_stacks/<name>/` template system
  (`available_stacks()`, `new_project()`). Add a stack by dropping in a folder.
- **`cloud-agnostic` stack** (default): nothing depends on a proprietary cloud
  service; everything is env-configured and Docker-orchestrated — ready for
  GCP / Azure / AWS / Oracle Cloud / VPS / dedicated / Kubernetes / Docker Swarm.
- **`SCAFFOLDING_GUIDE.md`** documentation.

### Changed
- The single `nx-ai-engineer` wheel now also bundles the `_stacks/` templates.
- Optional service layers (Redis, Nginx, worker, scheduler, Mailhog, MinIO,
  PgAdmin) and deep observability (OpenTelemetry) are documented as follow-up
  overlays on this base.

## [1.0.1] — 2026-06-24 · single self-contained distribution

**Packaging only — no behavior change.** The platform now publishes as **one
self-contained distribution**: a single `nx-ai-engineer` wheel that bundles every
`nx_*` module. `pip install nx-ai-engineer` carries the whole platform with no
sub-distributions on PyPI.

### Changed
- The root `pyproject.toml` builds one wheel that bundles all nine `nx_*` modules
  (via per-module `package-dir`) and owns the `nxai`/`nx` console scripts —
  replacing the previous metapackage that depended on nine separate `nxai-*`
  projects. Development still uses the 9-package `packages/` layout (verified by
  `scripts/verify_packages.py`); only the published artifact changed.
- `release.yml` builds and publishes only the single distribution.

### Fixed
- Publishing reliability: a single project means every release after the first is
  an *update*, never a brand-new-project creation — sidestepping PyPI's per-IP
  `429 Too many new projects created` limit that blocks publishing many new
  projects from shared GitHub Actions runner IPs.

## [1.0.0] — 2026-06-23 · first public platform release

**NX AI Engineer becomes a Developer Infrastructure Platform** — distributable via
PyPI, installable with a single `nxai` CLI, and prepared for long-term open-source
evolution. No engine behavior was removed; this release is about distribution,
packaging and the official product surface.

### Added
- **Database Engineering — Packs × Specialist Agents** (ADR-0021): a `database`
  pack category with `postgres` and `mongodb` authored in full (rules, patterns,
  **anti-patterns**, **performance**, security, checklists, migration template, agent
  prompt) plus mysql/sqlserver/oracle/sqlite/redis/cassandra/elastic/neo4j scaffolds.
  New **specialist agents** — `database-relational`, `database-nosql` and a
  read-only `database-reviewer` that runs a mandatory **Database Review** and
  **blocks** on duplicate tables, redundant indexes or anti-patterns. The same pack
  serves many agents via `applies_to` (knowledge reused, never duplicated); the
  agent executes, the pack holds the knowledge. `nxai pack list` now groups by
  category. Packs remain knowledge-only (no code, no AI).
- **Engineering Contract** — the concept that ties Brain/Knowledge/Context/Providers/
  Packs together and makes delivery to the agent *predictable*. An agent receives a
  declarative **contract** (`context · knowledge · engineering · constraints ·
  requirements · brain`), not an ad-hoc prompt:
  `Task → EngineeringContract → Context Builder → Model → Result → Knowledge Update`.
  **Engineering Packs are contracts**: each declares `applies_to` (agents or `"*"`)
  plus `required_adrs`/`mandatory_tests`/`validations`/`brain_facets`, so packs
  **auto-attach** to an agent (Backend automatically gets Security + LGPD +
  Multi-Tenant), with per-agent overrides in `config.json` (`contracts.agents`).
  The contract is **enforced at delivery** — a Governance/Delivery gate blocks
  shipping untested code when an applicable pack mandates tests, and the PR lists
  the contract's required validations/checklists. New `nxai contract` command,
  `KnowledgeEngine.build_contract`, `ContractBuilder`, ADR-0020 and
  `ENGINEERING_CONTRACT.md`.
- **Engineering Packs** — a new `nx-packs` package shipping a catalog of **domain
  knowledge bundles** (policies, patterns, checklists, ADRs, templates, examples,
  context) for engineering domains. Two reference packs are authored in full
  (**lgpd**, **security**/OWASP) plus structured scaffolds for owasp, ai, cloud,
  docker, multi-tenant, observability, testing, billing, authentication. Managed
  via `nxai pack <list|show|add|remove>`; once installed under `.ai-project-assistant/packs/`,
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
- **PyPI distribution.** `pip install nx-ai-engineer` installs the 9 `nx-*`
  packages and the `nxai` script — **no manual file copying**. The deployable
  template (agent specs, doc/code templates, project rules, guides, config
  example) ships as **package data** inside `nx-cli` (`nx_cli/_template/`).
- **Data-only `.ai-project-assistant/`.** The platform code lives in the installed packages;
  a project's `.ai-project-assistant/` holds **only data** (config + Brain + Vault +
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
  now falls back to `<cwd>/.ai-project-assistant` instead of pointing into the install tree;
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
  `website/` + `installer/`): the platform is split into **9 acyclic packages**
  (nx-core, nx-workflow, nx-sdk, nx-providers, nx-obsidian, nx-knowledge,
  nx-packs, nx-runtime, nx-cli), each an **independently importable** package.
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
  `packages/` into `<target>/.ai-project-assistant/`, and the deployed orchestrator shim
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
