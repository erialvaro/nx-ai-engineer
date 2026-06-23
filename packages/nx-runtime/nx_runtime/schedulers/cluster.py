"""Execution Cluster — the concurrent evolution of the Execution Engine.

Runs many agent nodes in parallel through a Worker Pool fed by an internal
priority Queue, while a Scheduler keeps dependencies, locks and readiness
correct. It REUSES the existing infrastructure rather than duplicating it:

- `NodeExecutor` (from execution.py)  — the single per-node execution logic
  (lock check, state transitions + events, runner call, retry). A shared
  `threading.Lock` makes its transitions/emits atomic; the runner call runs
  outside the lock, so agents truly execute concurrently.
- `TaskGraph` (kernel.lifecycle)      — dependency readiness, cycles, progress.
- `states` / `Node` / `Run`           — same domain + state machine.
- `BaseEngine` (kernel.engine)        — same Dry Run → Test → Execute gate.
- adapter/runner abstraction          — same as the engine (model-agnostic).

So the Cluster adds ONLY the new thing: a concurrent scheduler + worker pool.
Setting `max_workers=1` makes it behave like the sequential engine.
"""
from __future__ import annotations

import heapq
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..adapters.dryrun import DryRunAdapter
from nx_core.foundation import util
from nx_core.kernel.domain import Node, Run
from nx_core.kernel.engine import BaseEngine, EngineResult, ExecutionMode
from nx_core.kernel.lifecycle import TaskGraph
from nx_core.kernel.states import ExecutionState as S
from nx_core.kernel.states import transition
from .execution import (
    NodeExecutor, Runner, adapter_runner, build_graph, node_priority,
)


# --------------------------------------------------------------------------- #
# Worker lifecycle
# --------------------------------------------------------------------------- #
class WorkerState(str, Enum):
    CREATED = "CREATED"
    IDLE = "IDLE"
    BUSY = "BUSY"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


@dataclass
class Worker:
    id: int
    state: WorkerState = WorkerState.CREATED
    processed: int = 0
    current: Optional[str] = None
    thread: Optional[threading.Thread] = None

    def snapshot(self) -> dict[str, Any]:
        return {"id": self.id, "state": self.state.value,
                "processed": self.processed, "current": self.current}


@dataclass(order=True)
class _QueueItem:
    # Min-heap ordered by (-priority, seq) → higher priority first, FIFO on ties.
    sort_key: tuple = field(compare=True)
    node: Node = field(compare=False, default=None)


@dataclass
class ClusterPolicy:
    max_workers: int = 4
    max_retries: int = 1
    queue_timeout: float = 0.05  # worker poll interval (s)


# --------------------------------------------------------------------------- #
# The cluster
# --------------------------------------------------------------------------- #
class ExecutionCluster(BaseEngine):
    name = "execution-cluster"

    def __init__(self, *, runner: Optional[Runner] = None, adapter=None,
                 lock_provider=None, bus=None,
                 policy: Optional[ClusterPolicy] = None, persist: bool = False) -> None:
        super().__init__(bus=bus)
        self._adapter = adapter
        self._explicit_runner = runner
        self._locks = lock_provider
        self._policy = policy or ClusterPolicy()
        self._persist = persist
        self._cancel = threading.Event()
        self._mutex = threading.Lock()
        self.workers: list[Worker] = []
        self.last_run: Optional[Run] = None

    # -- public control surface ------------------------------------------ #
    def cancel(self) -> None:
        self._cancel.set()
        if self._adapter is not None and hasattr(self._adapter, "cancel"):
            try:
                self._adapter.cancel()
            except Exception:
                pass

    def progress(self) -> dict[str, int]:
        if not self.last_run:
            return {"total": 0}
        return TaskGraph(self.last_run.nodes).progress()

    def workers_status(self) -> list[dict[str, Any]]:
        return [w.snapshot() for w in self.workers]

    # -- engine modes (same gate as the sequential engine) --------------- #
    def _runner_for(self, mode: ExecutionMode) -> Runner:
        if self._explicit_runner is not None:
            return self._explicit_runner if mode is ExecutionMode.EXECUTE else _noop
        if self._adapter is not None:
            return adapter_runner(self._adapter, mode)
        if mode is ExecutionMode.EXECUTE:
            return adapter_runner(DryRunAdapter(), ExecutionMode.EXECUTE)
        return _noop

    def dry_run(self, ctx: Any) -> EngineResult:
        return self._result(ExecutionMode.DRY_RUN,
                            self._drive(ctx, self._runner_for(ExecutionMode.DRY_RUN), simulate=True))

    def test(self, ctx: Any) -> EngineResult:
        run = self._drive(ctx, self._runner_for(ExecutionMode.TEST), simulate=True)
        res = self._result(ExecutionMode.TEST, run)
        if any(n.state == S.FAILED for n in run.nodes):
            res.ok = False
            res.diagnostics.append("simulation produced FAILED nodes")
        return res

    def execute(self, ctx: Any) -> EngineResult:
        return self._result(ExecutionMode.EXECUTE,
                            self._drive(ctx, self._runner_for(ExecutionMode.EXECUTE), simulate=False))

    # -- concurrent scheduler -------------------------------------------- #
    def _drive(self, ctx: Any, runner: Runner, *, simulate: bool) -> Run:
        self._cancel.clear()
        graph = build_graph(ctx, self._policy.max_retries)
        run_id = util.short_hash(util.now_iso() + repr(ctx))
        plan_id = ctx.get("id") if isinstance(ctx, dict) else getattr(ctx, "id", "plan")
        plan_priority = ctx.get("priority", "normal") if isinstance(ctx, dict) else "normal"
        run = Run(id=run_id, plan_id=plan_id or "plan", nodes=graph.nodes,
                  status="running", started_at=util.now_iso())
        self.last_run = run
        self._bemit("run.started", {"run_id": run_id, "simulate": simulate,
                                    "workers": self._policy.max_workers}, run_id)

        executor = NodeExecutor(runner=runner, bus=self._bus, locks=self._locks,
                                owner=plan_id, run_id=run_id, mutex=self._mutex)

        # Shared coordination state (guarded by self._mutex).
        self._heap: list[_QueueItem] = []
        self._seq = 0
        self._queued: set[str] = set()
        self._inflight: set[str] = set()
        self._blocked_perm: set[str] = set()
        self._cond = threading.Condition(self._mutex)
        self._priority = {n.id: node_priority(n.subtask.agent, plan_priority) for n in graph.nodes}
        self._stopping = False  # set before workers start (avoids a startup race)

        n_workers = max(1, self._policy.max_workers)
        self.workers = [Worker(i) for i in range(n_workers)]
        threads = []
        for w in self.workers:
            t = threading.Thread(target=self._worker_loop, args=(w, executor, graph),
                                 name=f"aies-worker-{w.id}", daemon=True)
            w.thread = t
            w.state = WorkerState.IDLE
            t.start()
            threads.append(t)

        # Scheduler runs on the calling thread.
        self._schedule_loop(graph, run_id)

        # Stop workers and join.
        with self._cond:
            self._stopping = True
            self._cond.notify_all()
        for w in self.workers:
            w.state = WorkerState.STOPPING
        for t in threads:
            t.join(timeout=5)
        for w in self.workers:
            w.state = WorkerState.STOPPED

        # Cancellation wins: once cancelled, every remaining node is terminal too,
        # so check the cancel flag before is_done().
        if self._cancel.is_set():
            run.status = "cancelled"
        else:
            run.status = "done" if graph.is_done() else "stuck"
        run.ended_at = util.now_iso()
        run.metrics = graph.progress()
        run.metrics["workers"] = n_workers
        self._bemit("run.completed", {"run_id": run_id, "status": run.status,
                                      "metrics": run.metrics}, run_id)
        if self._persist and not simulate:
            self._save(run)
        return run

    def _schedule_loop(self, graph: TaskGraph, run_id: str) -> None:
        while True:
            with self._cond:
                if self._cancel.is_set():
                    self._cancel_remaining(graph, run_id)
                    return
                if graph.is_done():
                    return
                self._enqueue_ready(graph)
                # If nothing queued and nothing running, but not done → deadlock.
                if not self._heap and not self._inflight:
                    self._mark_deadlock(graph, run_id)
                    return
                # Wait until a worker finishes or a slot frees up.
                self._cond.wait(timeout=0.5)

    def _enqueue_ready(self, graph: TaskGraph) -> None:
        # Caller holds self._mutex (via self._cond).
        for node in graph.ready_nodes():
            nid = node.id
            if nid in self._queued or nid in self._inflight or nid in self._blocked_perm:
                continue
            self._seq += 1
            key = (-self._priority.get(nid, 0), self._seq)
            heapq.heappush(self._heap, _QueueItem(key, node))
            self._queued.add(nid)
        self._cond.notify_all()

    def _worker_loop(self, worker: Worker, executor: NodeExecutor, graph: TaskGraph) -> None:
        while True:
            with self._cond:
                while not self._heap and not self._stopping and not self._cancel.is_set():
                    self._cond.wait(timeout=0.5)
                if self._stopping or self._cancel.is_set():
                    worker.state = WorkerState.STOPPING
                    return
                item = heapq.heappop(self._heap)
                node = item.node
                self._queued.discard(node.id)
                self._inflight.add(node.id)
                worker.state = WorkerState.BUSY
                worker.current = node.id

            # Run the actual work OUTSIDE the lock → real concurrency.
            outcome = executor.attempt(node)

            with self._cond:
                self._inflight.discard(node.id)
                if outcome == S.BLOCKED.value:
                    self._blocked_perm.add(node.id)
                worker.processed += 1
                worker.current = None
                worker.state = WorkerState.IDLE
                self._cond.notify_all()  # wake scheduler to re-evaluate readiness

    def _mark_deadlock(self, graph: TaskGraph, run_id: str) -> None:
        for n in graph.pending_nodes():
            if n.state != S.BLOCKED:
                try:
                    transition(n, S.BLOCKED, reason="unsatisfiable dependency", bus=self._bus)
                except Exception:
                    pass

    def _cancel_remaining(self, graph: TaskGraph, run_id: str) -> None:
        # Called while the scheduler already holds the mutex (via the Condition),
        # so emit directly — never re-acquire the non-reentrant lock here.
        for n in graph.pending_nodes():
            try:
                transition(n, S.CANCELLED, reason="run cancelled", bus=self._bus)
                if self._bus is not None:
                    self._bus.emit("task.cancelled", {}, run_id=run_id, node_id=n.id)
            except Exception:
                pass

    # -- helpers (mirror the engine; emit under mutex) ------------------- #
    # NOTE: named `_bemit` (not `_emit`) so it does not clash with
    # BaseEngine._emit(event_type, payload), which the mode gate relies on.
    def _bemit(self, etype: str, payload: dict, run_id: str, node_id: Optional[str] = None) -> None:
        if self._bus is None:
            return
        with self._mutex:
            self._bus.emit(etype, payload, run_id=run_id, node_id=node_id)

    def _save(self, run: Run) -> None:
        try:
            util.write_json(util.config_root() / "runs" / f"{run.id}.json", run.as_dict())
        except Exception:
            pass

    def _result(self, mode: ExecutionMode, run: Run) -> EngineResult:
        ok = run.status == "done" and all(
            n.state in (S.COMPLETED, S.SKIPPED) for n in run.nodes)
        actions = [{"node": n.id, "agent": n.subtask.agent, "state": n.state.value,
                    "attempts": n.attempts} for n in run.nodes]
        diags = [f"{k}={v}" for k, v in run.metrics.items()]
        return EngineResult(mode=mode, ok=ok, actions=actions, diagnostics=diags)


def _noop(node: Node):
    from nx_core.kernel.domain import AgentResult
    return AgentResult(ok=True, notes="[simulated]")
