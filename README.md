# NX AI Engineer

**v1.0.0** · stdlib-only · zero runtime dependencies · 218 tests green ·
[CHANGELOG](CHANGELOG.md) · [ROADMAP](ROADMAP.md) · [RELEASE_NOTES](RELEASE_NOTES.md)

**NX AI Engineer is a Developer Infrastructure Platform for AI-assisted software
development.** Its job is to organize **knowledge, context and execution** so that
*any* AI model becomes dramatically more effective while building software.

> NX AI Engineer does **not** replace Claude Code, GPT, Gemini or any other model.
> **All intelligence belongs to the model. All organization belongs to NX.**

It installs like any modern tool — a package from PyPI and a single `nxai` CLI —
and works on any stack (Node, Python, Go, Rust, Java, Nx and other monorepos, …),
which it **discovers** at runtime.

> **Guides:**
> [Installer](packages/nx-cli/nx_cli/_template/docs/INSTALLER_GUIDE.md) ·
> [Upgrade](packages/nx-cli/nx_cli/_template/docs/UPGRADE_GUIDE.md) ·
> [Architecture](docs/ARCHITECTURE.md) ·
> [SDK](packages/nx-cli/nx_cli/_template/docs/SDK_GUIDE.md) ·
> [Engine](packages/nx-cli/nx_cli/_template/docs/ENGINE_GUIDE.md) ·
> [Workflow](packages/nx-cli/nx_cli/_template/docs/WORKFLOW_GUIDE.md) ·
> [Plugin](packages/nx-cli/nx_cli/_template/docs/PLUGIN_GUIDE.md) ·
> [Knowledge](packages/nx-cli/nx_cli/_template/docs/KNOWLEDGE_GUIDE.md) ·
> [Project Brain](packages/nx-cli/nx_cli/_template/docs/PROJECT_BRAIN.md) ·
> [Contributing](CONTRIBUTING.md)

## Install

```bash
pip install nx-ai-engineer
nxai version
nxai doctor
```

No manual file copying, ever. The platform code lives in the installed packages;
your project's `.ai-project/` holds **data only**.

## Quickstart

From the root of any repository:

```bash
nxai init                      # scaffold .ai-project + audit + Brain + Knowledge + Vault
nxai plan "Add OAuth login"    # plan a goal into a task (agents, order, locks)
nxai execute "Add OAuth login" # full end-to-end flow (Dry Run -> Test -> Execute; dry-run by default)
nxai review                    # consolidated diff review
nxai knowledge status          # the three memories: Brain / Obsidian / Git
nxai docs                      # the bundled guides
```

Everything is **safe by default**: execution always runs **Dry Run → Test →
Execute** and defaults to dry-run.

## What it does

NX turns a single request into a disciplined flow — never "implement immediately":

```
audit → discover → impact → risk → plan → subtasks → agents → order →
implement → test → review → consolidate → document → report
```

It coordinates **specialized agents** (backend, frontend, database, ai, security,
devops, qa, docs, plus read-only architect/planner/reviewer/delivery) that work
safely on the same codebase via advisory locks and isolated git worktrees.

### The three memories

| Memory | Component | Role |
|---|---|---|
| **Operational** | Project Brain (`brain/`) | Structured knowledge — **never code**, never model output. |
| **Organizational** | Obsidian Vault (`obsidian/`, folders `00 Dashboard`…`14 Retrospectives`) | A navigable, auto-synced visual reflection of the Brain. |
| **Historical** | Git (opt-in) | Immutable snapshots of the knowledge over time. |

The **Knowledge Engine** has exactly five responsibilities — *discover, index,
relate, update, deliver_context* — and **never reasons, learns programming, or
interprets code**. It only reduces the model's cognitive load: the richer the
project history, the sharper the model's work, the **fewer tokens** spent.

## CLI

| Command | Purpose |
|---|---|
| `nxai init` | Initialize `.ai-project` (scaffold + audit + Brain + Knowledge + Vault) |
| `nxai audit` | Discover & persist the architecture |
| `nxai plan "<goal>"` | Plan a goal into a task |
| `nxai execute "<goal>"` | Full end-to-end flow (alias of `pipeline`) |
| `nxai review` | Consolidated diff review |
| `nxai knowledge <index\|list\|retrieve\|sync\|status\|graph>` | Knowledge Engine + Providers |
| `nxai obsidian <sync\|status>` | Sync/inspect the Obsidian vault |
| `nxai pack <list\|show\|add\|remove>` | Engineering Packs (domain knowledge bundles) |
| `nxai graph` | Show the project Knowledge Graph |
| `nxai report` | Consolidated report (status + insights + metrics) |
| `nxai docs [name]` | List the bundled guides, or print one |
| `nxai doctor` | Health-check the install and project |
| `nxai update` | Refresh template assets (keeps Brain/Vault/config/history) |
| `nxai version` | Show version |

…plus `decide`, `dispatch`, `context`, `run`, `deliver`, `pipeline`, `metrics`,
`insights`, `recommend`, `worktree`, `tasks`, `locks`, `unlock`, `status`.
(The legacy `nx` alias is also installed.)

## Engineering Packs

Domain knowledge — not code — that makes the agents apply a domain's rules
correctly:

```bash
nxai pack list                 # browse the catalog
nxai pack add lgpd             # install LGPD/privacy policies + checklists + context
nxai pack add security         # OWASP/ASVS-aligned application security
```

Built-in packs: **lgpd**, **security** (stable) plus scaffolds for owasp, ai,
cloud, docker, multi-tenant, observability, testing, billing, authentication. Once
installed, the **Pack Provider** feeds the pack's policies/checklists/context to
the agents working in that domain. Packs contain **no code and no AI**. See the
[Packs Guide](packages/nx-cli/nx_cli/_template/docs/PACKS_GUIDE.md); third parties
can publish their own (the pack Marketplace).

## Architecture

A monorepo of **9 acyclic, stdlib-only packages**:

```
nx-core ← nx-workflow ← nx-sdk
nx-core ← nx-packs
nx-core ← nx-providers ← nx-obsidian ← nx-knowledge
{core, workflow, sdk, knowledge} ← nx-runtime ← nx-cli
```

| Package | Responsibility |
|---|---|
| `nx-core` | Kernel (domain/states/lifecycle/engine), governance, observability, foundation |
| `nx-workflow` | Reusable multi-step workflows |
| `nx-sdk` | Public extension surface (agents/engines/workflows/adapters/plugins/tools) |
| `nx-packs` | Engineering Packs catalog (domain knowledge bundles) |
| `nx-providers` | Knowledge providers (filesystem, git, markdown, ADR, project-brain, packs) + the relate/graph primitive |
| `nx-obsidian` | Obsidian provider + vault sync |
| `nx-knowledge` | Knowledge Engine, registry, memory (Brain), evolution |
| `nx-runtime` | Adapters, schedulers, intelligence, engines, composition-root pipeline |
| `nx-cli` | The official `nxai` CLI + the deployable template |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The acyclic graph is enforced by
`scripts/verify_packages.py`; the full Quality Gate is `scripts/quality_gate.py`.

## Extending

NX is built on an Open/Closed SDK — register agents, engines, workflows, adapters,
plugins and tools without touching the core. See the
[SDK Guide](packages/nx-cli/nx_cli/_template/docs/SDK_GUIDE.md) and
[Plugin Guide](packages/nx-cli/nx_cli/_template/docs/PLUGIN_GUIDE.md).

## Principles

- **All intelligence is the model's.** NX organizes; it never reasons.
- **Stdlib-only core** — zero third-party runtime dependencies.
- **Safe by default** — Dry Run → Test → Execute; nothing destructive without intent.
- **The Brain never stores code** — only structured knowledge.
- **Knowledge is leverage** — more history ⇒ better context ⇒ fewer tokens.

## License

MIT — see [LICENSE](LICENSE).
