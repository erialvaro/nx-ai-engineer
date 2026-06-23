# Plugin Guide

A **plugin** is a cohesive bundle of extensions — agents, engines, workflows,
tools, event handlers — registered together through a single `setup(sdk)` hook.
Plugins are how teams package reusable capability on top of AIES without forking
the core.

> Prerequisite: `SDK_GUIDE.md` (registration surface).

## Anatomy
A plugin is any object with a `name` and a `setup(sdk)` method:
```python
class SecurityPackPlugin:
    name = "security-pack"

    def setup(self, sdk):
        # register everything this plugin provides
        sdk.register_agent("pentester", {
            "title": "Pentester", "keywords": ["pentest", "vulnerability"],
            "route_globs": ["**/security/**"], "read_only": False,
        })
        sdk.register_tool("sast", lambda path: ["finding-1"])
        sdk.on("delivery.completed", self._on_delivery)

    def _on_delivery(self, event):
        ...  # e.g. trigger an external scan
```

## Loading
```python
import nx_sdk as sdk
sdk.register_plugin("security-pack", SecurityPackPlugin())  # setup() runs now
```
Loading is **explicit**. After this, the plugin's agents/tools/workflows are
resolvable via the SDK and participate in the pipeline (its event handlers are
attached to the pipeline bus at run start via `sdk.apply_event_handlers`).

## Where to load plugins
- In a small bootstrap script your project runs before the orchestrator, or
- From a custom CLI/entry point that imports your plugin module and registers it.

(There is intentionally **no** auto-discovery or remote loading — see Security.)

## Best practices
- Keep a plugin focused (one capability area).
- Reuse the contracts (`BaseEngine`, `AgentAdapter`, `SelectionStrategy`,
  `Resolver`, `SemanticIndex`) — don't reach into core internals.
- Make engines obey the Dry Run → Test → Execute gate.
- Ship tests for your plugin's public behavior.

## Security
Plugins are **trusted code**: `setup(sdk)` runs in-process. Only load plugins you
control or audit. AIES never loads plugins automatically or from the network.
Validate any external input your plugin consumes.

A runnable example: `examples/05_create_plugin.py`.
