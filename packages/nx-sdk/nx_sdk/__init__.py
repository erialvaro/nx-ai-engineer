"""SDK — public, stable surface for extending AIES without touching the core.

Supports registration of Agents, Engines, Workflows, Adapters, Plugins and Tools,
plus event subscription. In PR-0 this exposes the registries as lightweight,
in-memory stores; later PRs wire them into the dispatcher/execution/pipeline.

    import nx_sdk as sdk
    sdk.register_workflow(my_workflow)
    sdk.on("run.completed", my_handler)
"""
from __future__ import annotations

from typing import Any, Callable

__version__ = "2.0.1"

# In-memory registries. Engines/dispatcher/pipeline read from these.
_REGISTRIES: dict[str, dict[str, Any]] = {
    "agents": {},
    "engines": {},
    "workflows": {},
    "adapters": {},
    "plugins": {},
    "tools": {},
}
_EVENT_HANDLERS: list[tuple[str, Callable]] = []


def _register(kind: str, name: str, obj: Any) -> Any:
    if not name:
        raise ValueError(f"{kind} registration requires a name")
    _REGISTRIES[kind][name] = obj
    return obj


def register_agent(name: str, spec: Any) -> Any:
    return _register("agents", name, spec)


def register_engine(name: str, factory: Any) -> Any:
    return _register("engines", name, factory)


def register_workflow(workflow: Any) -> Any:
    name = getattr(workflow, "name", None) or (workflow.get("name") if isinstance(workflow, dict) else None)
    _register("workflows", name, workflow)
    # Also publish to the live workflow registry so the pipeline/CLI can use it.
    try:
        from nx_workflow.workflow import default_registry
        if hasattr(workflow, "steps"):
            default_registry().register(workflow)
    except Exception:
        pass
    return workflow


def register_adapter(name: str, adapter: Any) -> Any:
    return _register("adapters", name, adapter)


def register_plugin(name: str, plugin: Any) -> Any:
    """Register a plugin and run its `setup(sdk)` hook if present (a plugin bundles
    agents/engines/workflows/tools and wires them via this module)."""
    _register("plugins", name, plugin)
    setup = getattr(plugin, "setup", None)
    if callable(setup):
        import sys
        setup(sys.modules[__name__])
    return plugin


def register_tool(name: str, tool: Any) -> Any:
    return _register("tools", name, tool)


def on(event_type: str, handler: Callable) -> Callable:
    """Subscribe to an event type (or '*' for all). The pipeline attaches these to
    the live EventBus at run start."""
    _EVENT_HANDLERS.append((event_type, handler))
    return handler


def registry(kind: str) -> dict[str, Any]:
    return dict(_REGISTRIES.get(kind, {}))


def event_handlers() -> list[tuple[str, Callable]]:
    return list(_EVENT_HANDLERS)


# -- lookups (used by the pipeline/dispatcher/execution) ------------------- #
def get(kind: str, name: str) -> Any:
    return _REGISTRIES.get(kind, {}).get(name)


def get_adapter(name: str) -> Any:
    return get("adapters", name)


def get_tool(name: str) -> Any:
    return get("tools", name)


def get_workflow(name: str) -> Any:
    wf = get("workflows", name)
    if wf is not None:
        return wf
    try:
        from nx_workflow.workflow import default_registry
        return default_registry().get(name)
    except Exception:
        return None


def apply_event_handlers(bus) -> int:
    """Attach all SDK-registered event handlers to a live bus. Called by the
    Pipeline at start so third-party observers participate."""
    n = 0
    for event_type, handler in _EVENT_HANDLERS:
        bus.subscribe(event_type, handler)
        n += 1
    return n


def reset() -> None:
    """Clear all registries and handlers (test helper)."""
    for k in _REGISTRIES:
        _REGISTRIES[k].clear()
    _EVENT_HANDLERS.clear()


__all__ = [
    "register_agent", "register_engine", "register_workflow", "register_adapter",
    "register_plugin", "register_tool", "on", "registry", "event_handlers",
    "get", "get_adapter", "get_tool", "get_workflow", "apply_event_handlers", "reset",
]
