"""Execution Engine — drives a plan's nodes to completion.

Responsibilities (and ONLY these): read a plan, discover ready tasks, respect
dependencies and locks, control state, retries, failures, cancellation and
progress. It never implements project code: the actual work is delegated to an
injected `runner`/adapter, so the engine is fully generic and has zero knowledge
of agents or Claude Code.

It obeys the Engine contract: DRY_RUN and TEST simulate with a no-side-effect
runner; EXECUTE uses the injected adapter (which is the DryRunAdapter by default,
keeping execution safe unless a real adapter is provided). The mode gate from
`BaseEngine` is enforced — EXECUTE requires DRY_RUN + TEST first.
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Any, Callable, Optional

from nx_core import agents as agents_mod
from ..adapters.dryrun import DryRunAdapter
from nx_core.foundation import util
from nx_core.kernel.domain import AgentContext, AgentResult, Node, Run, subtasks_from_plan
from nx_core.kernel.engine import BaseEngine, EngineResult, ExecutionMode
from nx_core.kernel.lifecycle import TaskGraph
from nx_core.kernel.states import ExecutionState as S
from nx_core.kernel.states import transition

# Canonical priority order — earlier agents (contracts/data) outrank later ones
# when several nodes are ready at once. Single source of truth lives in agents.py.
_PRIORITY_ORDER = agents_mod.CANON_ORDER


def node_priority(agent: str, plan_priority: str = "normal") -> int:
    """Higher = more important. High-priority plans boost every node."""
    n = len(_PRIORITY_ORDER)
    base = n - (_PRIORITY_ORDER.index(agent) if agent in _PRIORITY_ORDER else n)
    return base + (100 if plan_priority == "high" else 0)


def build_graph(ctx: Any, max_retries: int) -> TaskGraph:
    """Build the dependency graph of Nodes from a plan/ctx. Shared by the
    sequential ExecutionEngine and the concurrent ExecutionCluster."""
    nodes = [Node(s, max_retries=max_retries) for s in subtasks_from_plan(ctx)]
    return TaskGraph(nodes)


@dataclass
class ExecutionPolicy:
    max_retries: int = 1
    continue_on_failure: bool = False


# A runner maps a node to an AgentResult. Adapters are wrapped into this shape.
Runner = Callable[[Node], AgentResult]


def adapter_runner(adapter, mode: Optional[ExecutionMode] = None) -> Runner:
    """Wrap an AgentAdapter into a node-level runner.

    `mode` is passed to the adapter only when it declares a `mode` parameter, so
    mode-aware adapters (e.g. ClaudeCodeAdapter) get the phase while legacy
    3-argument adapters keep working unchanged."""
    import inspect
    try:
        supports_mode = "mode" in inspect.signature(adapter.run).parameters
    except (TypeError, ValueError):
        supports_mode = False

    def _run(node: Node) -> AgentResult:
        ctx = AgentContext(agent=node.subtask.agent, subtask_id=node.id,
                           acceptance=node.subtask.acceptance)
        if supports_mode and mode is not None:
            return adapter.run(agent=node.subtask.agent, context=ctx,
                               instructions=node.subtask.objective, mode=mode)
        return adapter.run(agent=node.subtask.agent, context=ctx,
                           instructions=node.subtask.objective)
    return _run


def _noop_runner(node: Node) -> AgentResult:
    return AgentResult(ok=True, notes="[simulated]")


class NodeExecutor:
    """Single-node execution: lock check, state transitions (+events), runner
    invocation and retry bookkeeping. The ONE place this logic lives — reused by
    the sequential ExecutionEngine and the concurrent ExecutionCluster.

    Pass a `threading.Lock` as `mutex` to make state transitions and event emits
    atomic across worker threads; the runner call itself happens OUTSIDE the lock
    so real parallelism is preserved. Omit it for the single-threaded engine.
    """

    def __init__(self, *, runner: Runner, bus=None, locks=None,
                 owner: Optional[str] = None, run_id: str = "", mutex=None) -> None:
        self._runner = runner
        self._bus = bus
        self._locks = locks
        self._owner = owner
        self._run_id = run_id
        self._mutex = mutex or contextlib.nullcontext()

    def locked(self, node: Node) -> bool:
        if not self._locks:
            return False
        try:
            for area in node.subtask.areas:
                if self._locks.conflicts_for([area], owner_task=self._owner):
                    return True
        except Exception as exc:
            # Advisory locks: degrade to "not locked" but surface the failure
            # (never let a lock-subsystem bug pass unnoticed).
            if self._bus is not None:
                self._bus.emit("lock.check_error", {"error": repr(exc)})
            return False
        return False

    def _t(self, node: Node, to: S, reason: str = "") -> None:
        with self._mutex:
            transition(node, to, reason=reason, bus=self._bus)

    def _emit(self, etype: str, payload: dict, node_id: str) -> None:
        if self._bus is None:
            return
        with self._mutex:
            self._bus.emit(etype, payload, run_id=self._run_id, node_id=node_id)

    def attempt(self, node: Node) -> str:
        """Run one attempt of `node`. Returns the resulting state name
        (COMPLETED / FAILED / RETRYING / BLOCKED)."""
        if self._locks and self.locked(node):
            self._t(node, S.BLOCKED, "lock conflict")
            return S.BLOCKED.value

        self._t(node, S.READY)
        self._t(node, S.RUNNING, "dispatch")
        self._emit("task.started", {"agent": node.subtask.agent}, node.id)

        try:
            result = self._runner(node)
        except Exception as exc:  # a runner crash is a node failure, not a crash
            result = AgentResult(ok=False, error=repr(exc))

        with self._mutex:
            node.attempts += 1
            node.result = {"notes": result.notes, "changed_files": result.changed_files}

        if result.ok:
            self._t(node, S.COMPLETED)
            self._emit("task.completed", {"agent": node.subtask.agent}, node.id)
            return S.COMPLETED.value

        node.error = result.error
        self._t(node, S.FAILED, node.error or "failed")
        self._emit("task.failed", {"agent": node.subtask.agent, "error": node.error}, node.id)
        if node.attempts <= node.max_retries:
            self._t(node, S.RETRYING, f"attempt {node.attempts}")
            self._t(node, S.READY)
            self._emit("task.retrying", {"attempt": node.attempts}, node.id)
            return S.RETRYING.value
        return S.FAILED.value


class ExecutionEngine(BaseEngine):
    name = "execution"

    def __init__(self, *, runner: Optional[Runner] = None, adapter=None,
                 lock_provider=None, bus=None, policy: Optional[ExecutionPolicy] = None,
                 persist: bool = False) -> None:
        super().__init__(bus=bus)
        # `adapter` (mode-aware) takes precedence: dry/test/execute all delegate
        # to it with the right phase. A legacy explicit `runner` keeps the old
        # behavior (adapter used only in EXECUTE; dry/test simulate via noop).
        self._adapter = adapter
        if runner is not None:
            self._exec_runner = runner
        elif adapter is not None:
            self._exec_runner = adapter_runner(adapter, ExecutionMode.EXECUTE)
        else:
            self._exec_runner = adapter_runner(DryRunAdapter(), ExecutionMode.EXECUTE)
        self._locks = lock_provider
        self._policy = policy or ExecutionPolicy()
        self._persist = persist
        self._cancelled = False
        self._owner: Optional[str] = None  # task id whose own locks must not block it
        self.last_run: Optional[Run] = None

    # -- public control surface ------------------------------------------ #
    def cancel(self) -> None:
        self._cancelled = True
        # Propagate cancellation to a mode-aware adapter (e.g. kill in-flight CLI).
        if self._adapter is not None and hasattr(self._adapter, "cancel"):
            try:
                self._adapter.cancel()
            except Exception:
                pass

    def progress(self) -> dict[str, int]:
        if not self.last_run:
            return {"total": 0}
        return TaskGraph(self.last_run.nodes).progress()

    # -- engine modes ----------------------------------------------------- #
    def _mode_runner(self, mode: ExecutionMode) -> Runner:
        """A mode-aware adapter drives every phase; otherwise dry/test simulate."""
        if self._adapter is not None:
            return adapter_runner(self._adapter, mode)
        return _noop_runner

    def dry_run(self, ctx: Any) -> EngineResult:
        run = self._drive(ctx, runner=self._mode_runner(ExecutionMode.DRY_RUN), simulate=True)
        return self._result(ExecutionMode.DRY_RUN, run)

    def test(self, ctx: Any) -> EngineResult:
        # Validate the plan can be scheduled to completion with no real effects.
        run = self._drive(ctx, runner=self._mode_runner(ExecutionMode.TEST), simulate=True)
        res = self._result(ExecutionMode.TEST, run)
        if any(n.state == S.FAILED for n in run.nodes):
            res.ok = False
            res.diagnostics.append("simulation produced FAILED nodes")
        return res

    def execute(self, ctx: Any) -> EngineResult:
        run = self._drive(ctx, runner=self._exec_runner, simulate=False)
        return self._result(ExecutionMode.EXECUTE, run)

    # -- core scheduler --------------------------------------------------- #
    def _build_graph(self, ctx: Any) -> TaskGraph:
        return build_graph(ctx, self._policy.max_retries)

    def _drive(self, ctx: Any, *, runner: Runner, simulate: bool) -> Run:
        self._cancelled = False
        graph = self._build_graph(ctx)
        run_id = util.short_hash(util.now_iso() + repr(ctx))
        plan_id = ctx.get("id") if isinstance(ctx, dict) else getattr(ctx, "id", "plan")
        self._owner = plan_id  # a task never blocks on the locks its own plan created
        run = Run(id=run_id, plan_id=plan_id or "plan", nodes=graph.nodes,
                  status="running", started_at=util.now_iso())
        self.last_run = run
        if self._bus:
            self._bus.emit("run.started", {"run_id": run_id, "simulate": simulate},
                           run_id=run_id)

        # Shared per-node execution (single-threaded: no mutex needed).
        executor = NodeExecutor(runner=runner, bus=self._bus, locks=self._locks,
                                owner=self._owner, run_id=run_id)
        guard = 0
        limit = len(graph.nodes) * (self._policy.max_retries + 2) + 5
        while not graph.is_done() and guard < limit:
            guard += 1
            if self._cancelled:
                self._cancel_remaining(graph, run_id)
                break

            ready = graph.ready_nodes()
            if not ready:
                # Nothing ready but not done => remaining nodes are blocked.
                if self._mark_deadlock(graph, run_id):
                    break
                continue

            for node in ready:
                executor.attempt(node)

        run.status = "done" if graph.is_done() else "stuck"
        run.ended_at = util.now_iso()
        run.metrics = graph.progress()
        if self._bus:
            self._bus.emit("run.completed",
                           {"run_id": run_id, "status": run.status, "metrics": run.metrics},
                           run_id=run_id)
        if self._persist and not simulate:
            self._save(run)
        return run

    def _mark_deadlock(self, graph: TaskGraph, run_id: str) -> bool:
        """If no node is ready and some remain non-terminal, they are blocked by
        failed/cancelled deps. Mark them BLOCKED (or CANCELLED) and stop."""
        stuck = graph.pending_nodes()
        if not stuck:
            return True
        for n in stuck:
            if n.state not in (S.BLOCKED,):
                try:
                    transition(n, S.BLOCKED, reason="unsatisfiable dependency", bus=self._bus)
                except Exception:
                    pass
        return True

    def _cancel_remaining(self, graph: TaskGraph, run_id: str) -> None:
        for n in graph.pending_nodes():
            try:
                transition(n, S.CANCELLED, reason="run cancelled", bus=self._bus)
                if self._bus:
                    self._bus.emit("task.cancelled", {}, run_id=run_id, node_id=n.id)
            except Exception:
                pass

    def _save(self, run: Run) -> None:
        try:
            path = util.config_root() / "runs" / f"{run.id}.json"
            util.write_json(path, run.as_dict())
        except Exception:
            pass  # persistence is best-effort; never fail a run over it

    def _result(self, mode: ExecutionMode, run: Run) -> EngineResult:
        ok = run.status == "done" and all(
            n.state in (S.COMPLETED, S.SKIPPED) for n in run.nodes
        )
        actions = [{"node": n.id, "agent": n.subtask.agent, "state": n.state.value,
                    "attempts": n.attempts} for n in run.nodes]
        diags = [f"{k}={v}" for k, v in run.metrics.items()]
        return EngineResult(mode=mode, ok=ok, actions=actions, diagnostics=diags)
