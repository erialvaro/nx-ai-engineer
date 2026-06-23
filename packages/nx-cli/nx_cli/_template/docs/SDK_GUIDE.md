# SDK Guide

The SDK is the stable, public surface for extending AIES **without touching the
core**. Everything is registered into in-memory registries the platform reads at
run time.

```python
import nx_sdk as sdk
```

## What you can register
| Kind | Register with | Used by |
|------|---------------|---------|
| **Agent** | `sdk.register_agent(name, spec)` | Dispatcher/routing (also `config.json > extra_agents`) |
| **Engine** | `sdk.register_engine(name, factory)` | Workflow steps |
| **Workflow** | `sdk.register_workflow(workflow)` | Pipeline / `default_registry` |
| **Adapter** | `sdk.register_adapter(name, adapter)` | Execution (model independence) |
| **Plugin** | `sdk.register_plugin(name, plugin)` | bundles the above; runs `plugin.setup(sdk)` |
| **Tool** | `sdk.register_tool(name, tool)` | agents/engines that discover tools |
| **Event handler** | `sdk.on(event_type, handler)` | attached to the Pipeline bus |

Lookups: `sdk.get_adapter(name)`, `sdk.get_tool(name)`, `sdk.get_workflow(name)`,
`sdk.registry(kind)`, `sdk.apply_event_handlers(bus)`, `sdk.reset()`.

## Contracts you implement
- **Adapter** — `aies.adapters.base.AgentAdapter`
  (`run(agent, context, instructions, mode=…) -> AgentResult`).
- **Engine** — subclass `aies.kernel.engine.BaseEngine` (Dry Run → Test →
  Execute) or `ReadOnlyEngine`. See `ENGINE_GUIDE.md`.
- **Strategy** — `aies.schedulers.dispatcher.SelectionStrategy`.
- **Resolver** — `aies.memory.context.Resolver`.
- **Semantic index** — `aies.memory.semantic.SemanticIndex`.
- **Workflow** — `aies.workflow.workflow.Workflow`. See `WORKFLOW_GUIDE.md`.

## Examples (see `examples/` for runnable versions)

### Custom adapter (another model/CLI)
```python
import nx_sdk as sdk
from nx_core.kernel.domain import AgentResult

class MyModelAdapter:
    name = "my-model"
    def run(self, *, agent, context, instructions, mode=None):
        return AgentResult(ok=True, notes="done by my model")

sdk.register_adapter("my-model", MyModelAdapter())
```

### Custom selection strategy (rules → ML)
```python
from nx_runtime.schedulers.dispatcher import AgentDispatcher, AgentSelection

class MLStrategy:
    name = "ml"
    def select(self, *, description, registry):
        return [AgentSelection("backend", True, "ml pick", 0, [])]

AgentDispatcher(strategy=MLStrategy())
```

### Observe the pipeline
```python
import nx_sdk as sdk
sdk.on("delivery.completed", lambda e: print("delivered:", e.payload))
```

## Plugins
A plugin bundles agents/engines/workflows/tools and wires them via a `setup(sdk)`
hook. See **`PLUGIN_GUIDE.md`**.

## Security note
Registration runs in-process; **plugins are trusted code** loaded explicitly by
you. AIES never loads plugins automatically or from a remote source. Validate any
external input your extension consumes; the core never trusts external data.

## Guarantees
- Registration never mutates the core; `sdk.reset()` restores defaults.
- Stdlib-only core; your extensions may use anything, but keep the core clean.
