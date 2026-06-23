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
nxai pack add lgpd             # install into .ai-project/packs/lgpd/
nxai pack add security
nxai pack remove lgpd          # uninstall
```

Once installed, the **Pack Provider** (`nx_providers.knowledge.packs`) catalogs the
pack and the Context Engine feeds its **policies / checklists / context** to the
agents working in that domain — and reviewers can gate changes against the pack's
checklist. Installed packs live under `.ai-project/packs/<name>/` and are **data**
(never code), so `nxai update` and your project's git history treat them like any
other knowledge.

## Built-in catalog

| Pack | Domain | Status |
|---|---|---|
| `lgpd` | privacy / PII | **stable** |
| `security` | application security (OWASP/ASVS) | **stable** |
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
