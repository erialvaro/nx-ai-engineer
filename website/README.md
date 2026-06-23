# nx-ai-engineer — Website

Stdlib-only static site for the platform (no MkDocs/Docusaurus — the platform is
zero-dependency, and so is its site generator).

## Build

```
python website/generate.py [OUT_DIR]   # default: website/site/
```

`generate.py` collects the existing markdown and renders a static HTML site with
a shared nav:

- **Overview** — `README.md`, `ROADMAP.md`, `CHANGELOG.md`
- **Architecture** — `docs/ARCHITECTURE.md`, `docs/MIGRATION_PLAN.md`
- **Guides** — SDK / Engine / Workflow / Plugin / Knowledge / Project Brain /
  Project Knowledge / Architecture Overview / Migration (`packages/nx-cli/nx_cli/_template/docs/`)
- **ADRs** — every `packages/nx-cli/nx_cli/_template/docs/adr/ADR-*.md`
- **Packages** — a generated index of the 8 `packages/nx-*` (name, version, summary)

The generator implements a small markdown subset (headings, fenced code, lists,
blockquotes, tables, inline code/bold/links) — enough for the project docs, with
no third-party dependency. `tests/test_website.py` covers it.

The build output (`site/`) is a generated artifact and is gitignored.
