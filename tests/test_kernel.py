"""PR-1 — Kernel + EventBus tests: state machine, lifecycle/DAG, engine modes."""
import unittest

from nx_core.kernel.domain import Node, Subtask
from nx_core.kernel.engine import (
    BaseEngine, EngineResult, ExecutionMode, ModeGateError, ReadOnlyEngine,
)
from nx_core.kernel.lifecycle import CycleError, TaskGraph
from nx_core.kernel.states import (
    ExecutionState, InvalidTransition, can_transition, is_terminal, transition,
)
from nx_core.observability.events import Event, EventBus


def _node(nid, deps=None, state=ExecutionState.PENDING):
    return Node(Subtask(id=nid, agent=nid, depends_on=deps or []), state=state)


class TestStates(unittest.TestCase):
    def test_legal_and_illegal(self):
        self.assertTrue(can_transition(ExecutionState.READY, ExecutionState.RUNNING))
        self.assertFalse(can_transition(ExecutionState.COMPLETED, ExecutionState.RUNNING))

    def test_transition_emits_event(self):
        bus = EventBus()
        n = _node("backend")
        transition(n, ExecutionState.READY, bus=bus)
        self.assertEqual(n.state, ExecutionState.READY)
        self.assertEqual(len(bus.history("task.state_changed")), 1)

    def test_invalid_raises(self):
        n = _node("x", state=ExecutionState.COMPLETED)
        with self.assertRaises(InvalidTransition):
            transition(n, ExecutionState.RUNNING)

    def test_terminal(self):
        self.assertTrue(is_terminal(ExecutionState.COMPLETED))
        self.assertFalse(is_terminal(ExecutionState.READY))


class TestLifecycle(unittest.TestCase):
    def test_ready_respects_deps(self):
        a, b = _node("a"), _node("b", deps=["a"])
        g = TaskGraph([a, b])
        self.assertIn(a, g.ready_nodes())
        self.assertNotIn(b, g.ready_nodes())  # waits for a
        a.state = ExecutionState.COMPLETED
        self.assertIn(b, g.ready_nodes())

    def test_cycle_detected(self):
        a = _node("a", deps=["b"])
        b = _node("b", deps=["a"])
        with self.assertRaises(CycleError):
            TaskGraph([a, b])

    def test_progress_and_done(self):
        a, b = _node("a"), _node("b", deps=["a"])
        g = TaskGraph([a, b])
        self.assertFalse(g.is_done())
        a.state = ExecutionState.COMPLETED
        b.state = ExecutionState.SKIPPED
        self.assertTrue(g.is_done())
        self.assertEqual(g.progress()["total"], 2)


class _Spy(BaseEngine):
    name = "spy"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.calls = []

    def dry_run(self, ctx):
        self.calls.append("dry_run"); return EngineResult(ExecutionMode.DRY_RUN, True)

    def test(self, ctx):
        self.calls.append("test"); return EngineResult(ExecutionMode.TEST, True)

    def execute(self, ctx):
        self.calls.append("execute"); return EngineResult(ExecutionMode.EXECUTE, True)


class TestEngineModes(unittest.TestCase):
    def test_execute_blocked_without_prereqs(self):
        e = _Spy()
        with self.assertRaises(ModeGateError):
            e.run({"x": 1}, ExecutionMode.EXECUTE)

    def test_test_requires_dry_run(self):
        e = _Spy()
        with self.assertRaises(ModeGateError):
            e.run({"x": 1}, ExecutionMode.TEST)

    def test_full_cycle_order(self):
        e = _Spy()
        result = e.run_full_cycle({"x": 1})
        self.assertTrue(result.ok)
        self.assertEqual(e.calls, ["dry_run", "test", "execute"])

    def test_gate_is_per_context(self):
        e = _Spy()
        e.run({"a": 1}, ExecutionMode.DRY_RUN)
        e.run({"a": 1}, ExecutionMode.TEST)
        # different context must restart the gate
        with self.assertRaises(ModeGateError):
            e.run({"b": 2}, ExecutionMode.EXECUTE)

    def test_failed_mode_does_not_unlock_next(self):
        class FailDry(_Spy):
            def dry_run(self, ctx):
                return EngineResult(ExecutionMode.DRY_RUN, False)
        e = FailDry()
        e.run({"x": 1}, ExecutionMode.DRY_RUN)  # ok=False -> not marked passed
        with self.assertRaises(ModeGateError):
            e.run({"x": 1}, ExecutionMode.TEST)

    def test_readonly_engine_passes_all_modes(self):
        class Audit(ReadOnlyEngine):
            name = "audit"
            def analyze(self, ctx):
                return EngineResult(ExecutionMode.DRY_RUN, True, diagnostics=["ok"])
        a = Audit()
        self.assertTrue(a.run_full_cycle({}).ok)

    def test_modes_emit_events(self):
        bus = EventBus()
        e = _Spy(bus=bus)
        e.run_full_cycle({"x": 1})
        kinds = {ev.type for ev in bus.history()}
        self.assertTrue({"engine.dry_run", "engine.test", "engine.execute"} <= kinds)


class TestEventBus(unittest.TestCase):
    def test_pub_sub_and_wildcard(self):
        bus = EventBus()
        seen = []
        bus.subscribe("a.b", lambda e: seen.append(("specific", e.type)))
        bus.subscribe("*", lambda e: seen.append(("all", e.type)))
        bus.emit("a.b", {"k": 1})
        self.assertIn(("specific", "a.b"), seen)
        self.assertIn(("all", "a.b"), seen)

    def test_handler_error_is_isolated(self):
        bus = EventBus()
        def boom(e): raise RuntimeError("nope")
        bus.subscribe("x", boom)
        bus.emit("x")  # must not raise
        self.assertEqual(len(bus.history("bus.handler_error")), 1)


if __name__ == "__main__":
    unittest.main()
