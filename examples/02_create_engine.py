"""Example 2 — Create an Engine that obeys Dry Run -> Test -> Execute.

Run: python examples/02_create_engine.py
"""
from _bootstrap import aies_home  # noqa: F401  (sets up sys.path + AIES_HOME)

from nx_core.kernel.engine import BaseEngine, EngineResult, ExecutionMode
from nx_core.observability.events import EventBus


class GreetEngine(BaseEngine):
    name = "greet"

    def dry_run(self, ctx) -> EngineResult:
        # Simulate only — describe the action, change nothing.
        return EngineResult(ExecutionMode.DRY_RUN, ok=True,
                            actions=[{"would_greet": ctx["who"]}])

    def test(self, ctx) -> EngineResult:
        # Validate inputs safely.
        ok = bool(ctx.get("who"))
        return EngineResult(ExecutionMode.TEST, ok=ok,
                            diagnostics=["who is set"] if ok else ["who missing"])

    def execute(self, ctx) -> EngineResult:
        # Real effect (only reachable after dry_run + test passed).
        print(f"Hello, {ctx['who']}!")
        return EngineResult(ExecutionMode.EXECUTE, ok=True)


if __name__ == "__main__":
    bus = EventBus()
    engine = GreetEngine(bus=bus)

    # The gate blocks EXECUTE until DRY_RUN + TEST pass:
    try:
        engine.run({"who": "AIES"}, ExecutionMode.EXECUTE)
    except Exception as e:
        print("Gate blocked direct execute:", type(e).__name__)

    # Correct way — full cycle:
    result = engine.run_full_cycle({"who": "AIES"})
    print("full cycle ok:", result.ok)
    print("engine events:", sorted({e.type for e in bus.history()}))
