# Marketplace

NX AI Engineer is extended by two kinds of community artifact, each distributed as
an ordinary Python package on PyPI:

- **Engineering Packs** — domain *knowledge* bundles (policies, checklists,
  patterns, context). No code, no AI. See the [Packs Guide](PACKS_GUIDE.md).
- **Plugins** — *code* extensions that register agents, engines, workflows,
  adapters, providers or tools through the SDK. See the
  [Plugin Guide](PLUGIN_GUIDE.md) and [Provider SDK Guide](PROVIDER_SDK_GUIDE.md).

There is no central server: the "marketplace" is **PyPI + a naming convention +
a layout convention**. Discovery is `pip search`/PyPI; installation is `pip
install`. This keeps the trust model simple and explicit.

## Trust model

- Packs and plugins are **trusted code/knowledge you install on purpose**.
- NX **never** auto-discovers, downloads or executes remote artifacts. A plugin
  runs only when you register it; a pack is used only after `nxai pack add`.
- Vet third-party artifacts as you would any dependency.

## Naming convention

| Artifact | PyPI name | Example |
|---|---|---|
| Engineering Pack(s) | `nx-pack-<domain>` | `nx-pack-fintech` |
| Plugin | `nx-plugin-<name>` | `nx-plugin-jira` |
| Provider (inside a plugin) | provider `name` is kebab-case | `confluence` |

## Publishing an Engineering Pack package

Ship a package that mirrors the built-in `nx_packs` convention so the catalog is
discoverable the same way:

```
nx_pack_fintech/
  __init__.py            # exposes catalog(), names(), pack_dir(), manifest(), install()
  catalog/<name>/        # one dir per pack: pack.json + the standard layout
```

`catalog()` returns each pack's `pack.json`; `install(name, packs_root)` copies a
pack into a project's `.ai-project/packs/`. Reuse the reference implementation in
`nx_packs/__init__.py` (it is ~60 lines of stdlib). A pack package depends on
nothing but the standard library.

Each pack directory must contain at least `pack.json`, `README.md`, `context.md`,
`policies.md`, `checklists.md` and must contain **no `.py` files** (knowledge only).

## Publishing a Plugin package

A plugin is a class with a `setup(sdk)` hook that registers its components:

```python
class MyPlugin:
    name = "my-plugin"
    def setup(self, sdk):
        sdk.register_agent("my-agent", {...})
        sdk.register_provider(MyProvider())   # see the Provider SDK Guide
        sdk.on("pipeline.completed", my_handler)
```

Consumers load it explicitly in a small bootstrap (or your CLI entry point) via
`sdk.register_plugin(MyPlugin())`. NX never loads plugins automatically.

## Quality bar (recommended for listing)

- Stdlib-only where feasible; declare any third-party deps explicitly.
- Packs: knowledge only (no code/AI); pass `nxai pack show` cleanly.
- Plugins: no core mutation; `sdk.reset()` restores defaults; tests included.
- Semantic Versioning; a CHANGELOG; a clear README with install + usage.
- A license.

## Versioning & compatibility

Artifacts declare the NX major they target (e.g. `nx-core>=1,<2`). NX follows
[SemVer](https://semver.org): a breaking change to the SDK/provider contract lands
only in a new NX major, with a migration note.
