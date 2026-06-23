"""PR-2 — Execution Engine, adapters, workflow and ADR tests."""
import tempfile
import unittest
from pathlib import Path

from nx_runtime.adapters.base import AgentAdapter
from nx_runtime.adapters.dryrun import DryRunAdapter
from nx_core.governance import adr as adr_mod
from nx_core.kernel.engine import ExecutionMode, ModeGateError
from nx_core.kernel.states import ExecutionState as S
from nx_core.observability.events import EventBus
from nx_runtime.schedulers.execution import (
    ExecutionEngine, ExecutionPolicy, adapter_runner,
)
from nx_workflow.workflow import default_registry


def plan(*subtasks):
    return {"id": "t1", "subtasks": list(subtasks)}


def sub(agent, deps=None):
    return {"agent": agent, "objective": f"do {agent}", "areas": [],
            "depends_on": deps or [], "acceptance": ["tests pass"]}


class TestAdapters(unittest.TestCase):
    def test_dryrun_is_adapter(self):
        self.assertIsInstance(DryRunAdapter(), AgentAdapter)

    def test_dryrun_never_fails_by_default(self):
        from nx_core.kernel.domain import AgentContext
        r = DryRunAdapter().run(agent="backend",
                                context=AgentContext(agent="backend", subtask_id="backend"),
                                instructions="x")
        self.assertTrue(r.ok)
        self.assertEqual(r.changed_files, [])


class TestExecutionEngine(unittest.TestCase):
    def test_dry_run_completes_all(self):
        eng = ExecutionEngine()
        res = eng.run(plan(sub("database"), sub("backend", ["database"])), ExecutionMode.DRY_RUN)
        self.assertTrue(res.ok)
        self.assertTrue(all(n.state == S.COMPLETED for n in eng.last_run.nodes))

    def test_respects_dependency_order(self):
        bus = EventBus()
        order = []
        bus.subscribe("task.started", lambda e: order.append(e.payload["agent"]))
        eng = ExecutionEngine(bus=bus)
        eng.run(plan(sub("backend", ["database"]), sub("database")), ExecutionMode.DRY_RUN)
        self.assertLess(order.index("database"), order.index("backend"))

    def test_mode_gate_blocks_execute(self):
        eng = ExecutionEngine()
        with self.assertRaises(ModeGateError):
            eng.run(plan(sub("backend")), ExecutionMode.EXECUTE)

    def test_full_cycle_executes(self):
        eng = ExecutionEngine(runner=adapter_runner(DryRunAdapter()))
        res = eng.run_full_cycle(plan(sub("backend")))
        self.assertTrue(res.ok)

    def test_retry_then_success_is_not_possible_for_persistent_failure(self):
        # An agent that always fails should end FAILED after exhausting retries.
        eng = ExecutionEngine(runner=adapter_runner(DryRunAdapter(fail_agents={"backend"})),
                              policy=ExecutionPolicy(max_retries=2))
        eng.run(plan(sub("backend")), ExecutionMode.DRY_RUN)  # dry uses noop -> ok
        # In execute path the failing adapter is used:
        eng2 = ExecutionEngine(runner=adapter_runner(DryRunAdapter(fail_agents={"backend"})),
                               policy=ExecutionPolicy(max_retries=2))
        eng2.run(plan(sub("backend")), ExecutionMode.DRY_RUN)
        eng2.run(plan(sub("backend")), ExecutionMode.TEST)
        res = eng2.run(plan(sub("backend")), ExecutionMode.EXECUTE)
        self.assertFalse(res.ok)
        node = eng2.last_run.nodes[0]
        self.assertEqual(node.state, S.FAILED)
        self.assertEqual(node.attempts, 3)  # initial + 2 retries

    def test_dependent_of_failure_is_blocked(self):
        runner = adapter_runner(DryRunAdapter(fail_agents={"database"}))
        eng = ExecutionEngine(runner=runner, policy=ExecutionPolicy(max_retries=0))
        eng.run(plan(sub("database"), sub("backend", ["database"])), ExecutionMode.DRY_RUN)
        eng.run(plan(sub("database"), sub("backend", ["database"])), ExecutionMode.TEST)
        eng.run(plan(sub("database"), sub("backend", ["database"])), ExecutionMode.EXECUTE)
        states = {n.subtask.agent: n.state for n in eng.last_run.nodes}
        self.assertEqual(states["database"], S.FAILED)
        self.assertEqual(states["backend"], S.BLOCKED)

    def test_progress_counts(self):
        eng = ExecutionEngine()
        eng.run(plan(sub("a"), sub("b")), ExecutionMode.DRY_RUN)
        prog = eng.progress()
        self.assertEqual(prog["total"], 2)
        self.assertEqual(prog.get("COMPLETED"), 2)


class TestWorkflow(unittest.TestCase):
    def test_builtin_registered(self):
        reg = default_registry()
        self.assertIn("execute-plan", reg.names())
        self.assertEqual(reg.get("execute-plan").step_names(), ["execute"])


class TestADR(unittest.TestCase):
    def test_create_and_number(self):
        with tempfile.TemporaryDirectory() as d:
            dirp = Path(d)
            a1 = adr_mod.create("First decision", context="c", decision="d", directory=dirp)
            a2 = adr_mod.create("Second decision", context="c", decision="d", directory=dirp)
            self.assertEqual(a1["number"], 1)
            self.assertEqual(a2["number"], 2)
            self.assertTrue(Path(a2["path"]).exists())

    def test_event_driven_adr(self):
        with tempfile.TemporaryDirectory() as d:
            bus = EventBus()
            # patch dir resolution for the test
            import nx_core.governance.adr as g
            orig = g.adr_dir
            g.adr_dir = lambda: Path(d)
            try:
                adr_mod.subscribe(bus)
                bus.emit("decision.recorded", {"title": "Use event bus", "decision": "yes"})
                self.assertEqual(len(list(Path(d).glob("ADR-*.md"))), 1)
                self.assertEqual(len(bus.history("adr.created")), 1)
            finally:
                g.adr_dir = orig


if __name__ == "__main__":
    unittest.main()
