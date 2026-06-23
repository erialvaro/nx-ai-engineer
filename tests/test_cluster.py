"""Prompt-2 — Execution Cluster: worker pool, queue, scheduler, concurrency,
priorities, retry, cancel, dependencies, worker lifecycle."""
import threading
import time
import unittest

from nx_core.kernel.domain import AgentResult
from nx_core.kernel.engine import ExecutionMode, ModeGateError
from nx_core.kernel.states import ExecutionState as S
from nx_core.observability.events import EventBus
from nx_runtime.schedulers.cluster import (
    ClusterPolicy, ExecutionCluster, Worker, WorkerState,
)


def _ctx(agents, priority="normal", deps=None):
    deps = deps or {}
    return {"id": "t", "priority": priority, "subtasks": [
        {"agent": a, "objective": f"do {a}", "areas": [],
         "depends_on": deps.get(a, []), "acceptance": []} for a in agents]}


def ok_runner(node):
    return AgentResult(ok=True, notes="ok")


class TestParityWithEngine(unittest.TestCase):
    def test_completes_all_and_respects_deps(self):
        order, lock = [], threading.Lock()

        def rec(node):
            with lock:
                order.append(node.subtask.agent)
            return AgentResult(ok=True)

        ctx = _ctx(["backend", "database"], deps={"backend": ["database"]})
        c = ExecutionCluster(runner=rec, policy=ClusterPolicy(max_workers=4))
        res = c.run_full_cycle(ctx)
        self.assertTrue(res.ok)
        self.assertTrue(all(n.state == S.COMPLETED for n in c.last_run.nodes))
        self.assertLess(order.index("database"), order.index("backend"))

    def test_mode_gate_enforced(self):
        c = ExecutionCluster(runner=ok_runner)
        with self.assertRaises(ModeGateError):
            c.run(_ctx(["backend"]), ExecutionMode.EXECUTE)


class TestConcurrency(unittest.TestCase):
    def test_parallel_faster_than_sequential(self):
        def slow(node):
            time.sleep(0.15)
            return AgentResult(ok=True)
        ctx = _ctx(["backend", "frontend", "database", "devops"])

        t0 = time.time()
        ExecutionCluster(runner=slow, policy=ClusterPolicy(max_workers=1)).run_full_cycle(ctx)
        seq = time.time() - t0

        t0 = time.time()
        ExecutionCluster(runner=slow, policy=ClusterPolicy(max_workers=4)).run_full_cycle(ctx)
        par = time.time() - t0

        self.assertLess(par, seq * 0.7)  # parallel clearly faster

    def test_observed_max_parallelism(self):
        active = {"n": 0, "max": 0}
        lock = threading.Lock()

        def watch(node):
            with lock:
                active["n"] += 1
                active["max"] = max(active["max"], active["n"])
            time.sleep(0.1)
            with lock:
                active["n"] -= 1
            return AgentResult(ok=True)

        ctx = _ctx(["backend", "frontend", "database", "devops", "ai"])
        ExecutionCluster(runner=watch, policy=ClusterPolicy(max_workers=3)).run_full_cycle(ctx)
        self.assertGreaterEqual(active["max"], 2)   # genuinely concurrent
        self.assertLessEqual(active["max"], 3)      # never exceeds the pool


class TestPriorities(unittest.TestCase):
    def test_higher_priority_runs_first_with_one_worker(self):
        order, lock = [], threading.Lock()

        def rec(node):
            with lock:
                order.append(node.subtask.agent)
            return AgentResult(ok=True)

        # All independent and ready at once; 1 worker → strict priority order.
        ctx = _ctx(["docs", "architect", "frontend", "database"])
        ExecutionCluster(runner=rec, policy=ClusterPolicy(max_workers=1)).run_full_cycle(ctx)
        # architect & database outrank frontend & docs (canonical order).
        self.assertLess(order.index("architect"), order.index("docs"))
        self.assertLess(order.index("database"), order.index("frontend"))


class TestRetry(unittest.TestCase):
    def test_retry_until_success(self):
        seen = {}
        lock = threading.Lock()

        def flaky(node):
            with lock:
                seen[node.id] = seen.get(node.id, 0) + 1
                n = seen[node.id]
            return AgentResult(ok=n >= 2, error=None if n >= 2 else "transient")

        ctx = _ctx(["backend"])
        c = ExecutionCluster(runner=flaky, policy=ClusterPolicy(max_workers=2, max_retries=3))
        res = c.run_full_cycle(ctx)
        self.assertTrue(res.ok)
        self.assertEqual(c.last_run.nodes[0].state, S.COMPLETED)
        self.assertEqual(c.last_run.nodes[0].attempts, 2)

    def test_persistent_failure_ends_failed_and_blocks_dependent(self):
        def fail_db(node):
            return AgentResult(ok=node.subtask.agent != "database", error="boom")

        ctx = _ctx(["database", "backend"], deps={"backend": ["database"]})
        c = ExecutionCluster(runner=fail_db, policy=ClusterPolicy(max_workers=4, max_retries=0))
        c.run_full_cycle(ctx)
        states = {n.subtask.agent: n.state for n in c.last_run.nodes}
        self.assertEqual(states["database"], S.FAILED)
        self.assertEqual(states["backend"], S.BLOCKED)


class TestCancel(unittest.TestCase):
    def test_cancel_mid_run(self):
        c = ExecutionCluster(policy=ClusterPolicy(max_workers=1))
        calls = {"n": 0}

        def cancel_after_first(node):
            calls["n"] += 1
            if calls["n"] == 1:
                c.cancel()
            time.sleep(0.05)
            return AgentResult(ok=True)

        c._explicit_runner = cancel_after_first
        ctx = _ctx(["architect", "backend", "frontend", "qa"])
        run = c._drive(ctx, cancel_after_first, simulate=False)
        self.assertEqual(run.status, "cancelled")
        self.assertTrue(any(n.state == S.CANCELLED for n in run.nodes))


class TestWorkerLifecycle(unittest.TestCase):
    def test_workers_created_and_stopped(self):
        c = ExecutionCluster(runner=ok_runner, policy=ClusterPolicy(max_workers=3))
        c.run_full_cycle(_ctx(["backend", "frontend", "qa"]))
        states = [w.state for w in c.workers]
        self.assertEqual(len(c.workers), 3)
        self.assertTrue(all(s == WorkerState.STOPPED for s in states))
        self.assertEqual(sum(w.processed for w in c.workers), 3)

    def test_worker_snapshot_shape(self):
        w = Worker(0)
        snap = w.snapshot()
        self.assertEqual(set(snap), {"id", "state", "processed", "current"})


class TestEvents(unittest.TestCase):
    def test_emits_run_and_task_events(self):
        bus = EventBus()
        c = ExecutionCluster(runner=ok_runner, bus=bus, policy=ClusterPolicy(max_workers=2))
        c.run_full_cycle(_ctx(["backend", "qa"], deps={"qa": ["backend"]}))
        kinds = {e.type for e in bus.history()}
        self.assertTrue({"run.started", "run.completed", "task.started",
                         "task.completed", "task.state_changed"} <= kinds)
        started = bus.history("run.started")[-1]
        self.assertEqual(started.payload["workers"], 2)


if __name__ == "__main__":
    unittest.main()
