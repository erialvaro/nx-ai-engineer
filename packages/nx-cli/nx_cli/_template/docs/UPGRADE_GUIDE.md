# Upgrade Guide

Upgrading NX AI Engineer is a two-step operation that **never** risks your
project's accumulated knowledge.

## 1. Upgrade the platform (code)

```bash
pip install -U nx-ai-engineer
```

This replaces the installed `nx_*` packages with the new version. No project files
are touched.

## 2. Refresh the template assets

From a project's root:

```bash
nxai update
```

`update` refreshes only the **template-derived assets** that ship with the
platform — the framework agent specs, the doc/code templates, the project rules,
and `config.example.json`. It force-overwrites those files with the new versions.

### What `update` NEVER touches

By contract, `nxai update` will never modify, prune or overwrite:

- `config.json` — your configuration
- `brain/` — the Project Brain (operational memory)
- `obsidian/` — the Obsidian vault (organizational memory)
- `knowledge/` — indexed knowledge
- `tasks/`, `locks/`, `reviews/`, `logs/`, `memory/` — your working state & history

Your custom files (e.g. project-specific agent specs you added) are left in place;
only the files that came from the template are refreshed.

## Verifying an upgrade

```bash
nxai version    # confirm the new version
nxai doctor     # confirm packages align and the project is healthy
```

`nxai doctor` flags a version mismatch between packages, an unreadable
`config.json`, or a missing/locked `.ai-project-assistant/`.

## Semantic Versioning

NX AI Engineer follows [SemVer](https://semver.org):

- **patch** (`1.0.x`) — fixes, docs, internal improvements. Safe to upgrade.
- **minor** (`1.x.0`) — new, additive capabilities. Backward compatible.
- **major** (`x.0.0`) — a breaking change. Read the [Migration Guide](MIGRATION_GUIDE.md)
  and the CHANGELOG before upgrading; a migration path is always provided.

## Rolling back

Because the code lives in the installed packages and your data lives in
`.ai-project-assistant/`, rolling back the platform is just:

```bash
pip install nx-ai-engineer==<previous-version>
```

Your Brain, Vault, knowledge and history remain intact across rollbacks.
