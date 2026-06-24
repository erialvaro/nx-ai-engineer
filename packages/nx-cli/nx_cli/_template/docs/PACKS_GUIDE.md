# Engineering Packs Guide

An **Engineering Pack** is a bundle of **domain knowledge** — policies, patterns,
checklists, ADRs, templates, examples and a distilled *context* — for a single
engineering domain (e.g. LGPD/privacy, security, multi-tenancy, billing).

A pack contains **no product code and no AI**. It exists so that *any* model
applies a domain's rules correctly: NX organizes the knowledge; the model reasons.

## Using packs

```bash
nxai pack list                 # browse the catalog (installed packs are marked)
nxai pack show security        # read a pack's manifest + README
nxai pack add lgpd             # install into .ai-project-assistant/packs/lgpd/
nxai pack add security
nxai pack remove lgpd          # uninstall
```

Once installed, the **Pack Provider** (`nx_providers.knowledge.packs`) catalogs the
pack and the Context Engine feeds its **policies / checklists / context** to the
agents working in that domain — and reviewers can gate changes against the pack's
checklist. Installed packs live under `.ai-project-assistant/packs/<name>/` and are **data**
(never code), so `nxai update` and your project's git history treat them like any
other knowledge.

## Built-in catalog

| Pack | Domain | Status |
|---|---|---|
| `lgpd` | privacy / PII | **stable** |
| `security` | application security (OWASP/ASVS) | **stable** |
| `repo-standards` | repo governance + CI + templates (used by `nxai scaffold`) | **stable** |
| `owasp` | OWASP Top 10 mapping | scaffold |
| `ai` | safe AI/LLM integration | scaffold |
| `cloud` | cloud architecture | scaffold |
| `docker` | containers | scaffold |
| `multi-tenant` | tenant isolation | scaffold |
| `observability` | logs/metrics/traces | scaffold |
| `testing` | test strategy | scaffold |
| `billing` | money/payments | scaffold |
| `authentication` | authn & sessions | scaffold |

*Scaffold* packs are structured starting points seeded with real domain bullets —
expand their sections for your project.

## Repository scaffolding (`nxai scaffold`)

The **repo-standards** pack is special: besides its policies/checklists it ships a
`scaffold/` tree of concrete files that `nxai scaffold` lays into a project's repo
root — governance files (`CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`,
`.editorconfig`), `.github/` issue & PR templates, a `.gitignore`, and a CI
workflow matched to the stack (Python/Node/Go/generic).

```bash
nxai scaffold --stack auto --dry-run   # preview (auto-detects the stack from the audit)
nxai scaffold --stack python           # write the files (skips existing)
nxai scaffold --force                  # overwrite existing files
```

It is **idempotent** and never overwrites a file without `--force`. CI templates
are stored under neutral paths inside the pack and mapped to `.github/workflows/`
only when written into your project.

## Pack layout

Every pack is a directory with a `pack.json` manifest and these files:

```
<pack>/
  pack.json        # name, title, version, domain, summary, tags, status, provides
  README.md        # documentation
  context.md       # the distilled brief fed to agents   ← context surface
  policies.md      # enforceable rules                    ← context surface
  checklists.md    # review gate                          ← context surface
  patterns.md      # recommended approaches
  architecture.md  # structural guidance
  adr/             # domain ADRs
  templates/       # review/code/doc templates
  examples/        # worked examples
  tests/           # test guidance for the domain
```

The three **context surfaces** (`context.md`, `policies.md`, `checklists.md`) are
what the Pack Provider exposes to agent context.

## Packs (knowledge) × Specialist Agents (execution)

A pack is **knowledge**; a **Specialist Agent** *executes* using it. They are two
layers — the agent is disposable, the knowledge is the asset:

```
Database Engineering Pack (postgres)  →  knowledge (rules/patterns/anti-patterns/…)
        ↓ applies_to
Relational Database Agent             →  executes using that knowledge
```

The **same pack serves many agents** (Relational, Reviewer, Migration, Performance)
— no duplicated knowledge. The Engineering Contract decides which packs and which
agents each task involves (`applies_to` + `config.json` overrides).

### The Database category

`nxai pack list` groups packs by `category`. The **database** category ships:

| Pack | Engine | Status |
|---|---|---|
| `postgres` | PostgreSQL (relational) | **stable** |
| `mongodb` | MongoDB (NoSQL/document) | **stable** |
| `mysql`, `sqlserver`, `oracle`, `sqlite` | relational | scaffold |
| `redis`, `cassandra`, `elastic`, `neo4j` | key-value / wide-column / search / graph | scaffold |

Each database pack adds engine-specific knowledge beyond the standard files:
`patterns.md`, `anti-patterns.md`, `performance.md`, `security.md`,
`templates/migration.md` and `prompts/specialist.md`.

Specialist agents: **database-relational**, **database-nosql**, and a read-only
**database-reviewer** that runs the mandatory **Database Review** before any
migration — it never implements; it asks (similar table? similar index? composite
PK? redundancy? anti-pattern?) and **blocks** when a pack rule is violated:

```
Task → Database Review → Engineering Contract → Agent → Migration → Reviewer → EXPLAIN ANALYZE → Deliver
```

## Authoring a pack

1. Create a directory with the layout above and a valid `pack.json`
   (`status: "stable"` once complete, `"scaffold"` while in progress).
2. Keep it **knowledge only** — no source code, no AI. (`nxai pack` and the test
   suite enforce that packs contain no `.py` files.)
3. Built-in packs live in the `nx-packs` package catalog
   (`packages/nx-packs/nx_packs/catalog/<name>/`).

## Shipping your own packs (Marketplace)

Third parties can distribute packs as **their own Python package** that follows
the same `pack.json` + layout convention and exposes a `catalog()` / `install()`
API (mirroring `nx_packs`). This is the basis of the pack **Marketplace / Provider
SDK** — packs are discovered and installed exactly like the built-in catalog, with
no change to the core. See the [SDK Guide](SDK_GUIDE.md).
