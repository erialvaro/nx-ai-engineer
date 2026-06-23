"""Pipeline — the single end-to-end flow that integrates every engine.

request → Audit → Plan(Intelligence) → Dispatch → Context → Execute → Review →
Deliver → Learn → Brain.update → Experience.record

It wires one EventBus and attaches the cross-cutting listeners (Learning,
Experience, ADR). Each stage is observable. The default adapter is the
DryRunAdapter, so the pipeline is safe to run end-to-end without mutating code.
No stage is skipped; selection of *which agents* run is the Dispatcher's job.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from nx_core import analyzer, config as config_mod, planner, review as review_mod
from ..adapters.dryrun import DryRunAdapter
from ..engines import delivery as delivery_mod
from nx_core.experience.metrics import ExperienceRecorder
from nx_core.governance import adr as adr_mod
from nx_knowledge.memory.brain import ProjectBrain
from nx_knowledge.memory.context import ContextBuilder
from nx_knowledge.evolution.self_improvement import SelfImprovementEngine
from nx_core.observability.events import EventBus
from nx_core.observability.logging import EventLogger
from nx_core.observability.telemetry import Telemetry
from ..schedulers.execution import ExecutionEngine
from nx_core.kernel.domain import subtasks_from_plan
from nx_core.kernel.engine import ExecutionMode


@dataclass
class PipelineResult:
    request: str
    mode: str
    architecture: str = ""
    selected_agents: list[str] = field(default_factory=list)
    skipped_agents: list[str] = field(default_factory=list)
    context_reduction: dict[str, float] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    review: dict[str, Any] = field(default_factory=dict)
    delivery: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    brain_version: int = 0
    experience: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__


class Pipeline:
    def __init__(self, *, adapter=None, bus: Optional[EventBus] = None,
                 config: Optional[dict] = None, record_adr: bool = False,
                 max_workers: int = 1) -> None:
        self.bus = bus or EventBus()
        self.config = config or config_mod.load()
        self.adapter = adapter or DryRunAdapter()
        self.max_workers = max(1, max_workers)
        self.brain = ProjectBrain()
        # Autonomous learning: supersedes the basic LearningEngine — it records a
        # richer retrospective (time/failures/rework/agents/files/decisions/
        # strategy success) and evolves the Brain after each run.
        self.improvement = SelfImprovementEngine(self.brain, bus=self.bus)
        # Knowledge Engine: the single coordination point for the three memories
        # (Brain=operational, Obsidian=organizational, Git=historical). Attached
        # AFTER learning so it syncs the post-run Brain. Best-effort; also the
        # access point the Context Engine retrieves through.
        try:
            from nx_knowledge.knowledge.engine import KnowledgeEngine
            self.knowledge = KnowledgeEngine(self.brain, config=self.config, bus=self.bus)
        except Exception as exc:
            # Degrade gracefully (context still builds) but make it visible.
            self.knowledge = None
            self.bus.emit("knowledge.unavailable", {"error": repr(exc)})
        self.experience = ExperienceRecorder(bus=self.bus)
        self.logger = EventLogger(bus=self.bus)
        self.telemetry = Telemetry(bus=self.bus)
        # Attach any SDK-registered third-party event handlers.
        try:
            from nx_sdk import sdk
            sdk.apply_event_handlers(self.bus)
        except Exception as exc:
            self.bus.emit("sdk.handlers_error", {"error": repr(exc)})
        if record_adr:
            adr_mod.subscribe(self.bus)
        self._record_adr = record_adr

    def run(self, request: str, *, mode: ExecutionMode = ExecutionMode.DRY_RUN,
            base: str = "HEAD") -> PipelineResult:
        self.bus.emit("pipeline.started", {"request": request, "mode": mode.value})
        res = PipelineResult(request=request, mode=mode.value)

        # 1) Audit ------------------------------------------------------- #
        mem = analyzer.run_and_persist(config=self.config)
        arch = mem["architecture"]
        res.architecture = mem["audit"].get("summary", "")
        self.brain.migrate_legacy()

        # 2) Plan (Intelligence) ---------------------------------------- #
        plan = planner.build_plan(request, arch, self.config)

        # 3) Decide (intelligence): agents, workflow, order, risk, cost/time,
        #    review/QA, parallelism. Reuses the dispatcher internally. -------- #
        from ..intelligence.decision import DecisionEngine
        decision = DecisionEngine(bus=self.bus).decide(
            request, arch=arch, config=self.config, record_adr=self._record_adr)
        selections = decision.selections
        selected = set(decision.agents)
        res.selected_agents = decision.agents
        res.skipped_agents = decision.skipped
        res.decision = decision.summary()

        # 4) Context per selected agent --------------------------------- #
        # Context retrieves through the shared Knowledge Engine (one access point).
        builder = ContextBuilder(bus=self.bus, knowledge=self.knowledge)
        for sub in subtasks_from_plan(plan):
            if sub.agent in selected:
                try:
                    cr = builder.build(agent=sub.agent, subtask=sub,
                                       config=self.config, arch=arch)
                    res.context_reduction[sub.agent] = cr.estimated_reduction
                except Exception:
                    pass  # context is best-effort; never blocks the pipeline

        # 5) Execute (only selected subtasks; deps filtered to selected) - #
        # Pass the adapter so the full Dry Run → Test → Execute lifecycle flows
        # through it (mode-aware). DryRunAdapter (default) stays side-effect-free.
        exec_ctx = self._exec_ctx(request, plan, selected)
        if self.max_workers > 1:
            from ..schedulers.cluster import ClusterPolicy, ExecutionCluster
            engine = ExecutionCluster(bus=self.bus, adapter=self.adapter,
                                      policy=ClusterPolicy(max_workers=self.max_workers))
        else:
            engine = ExecutionEngine(bus=self.bus, adapter=self.adapter)
        self._drive_modes(engine, exec_ctx, mode)
        res.execution = {"status": engine.last_run.status if engine.last_run else "n/a",
                         "metrics": engine.progress()}

        # 6) Review ------------------------------------------------------ #
        report = review_mod.build(base, self.config)
        res.review = {"total_changed": report["total_changed"],
                      "without_tests": len(report["without_tests"]),
                      "critical": len(report["critical_changes"])}
        self.bus.emit("review.completed", {"findings": report["total_changed"],
                                           "without_tests": len(report["without_tests"]),
                                           "critical": len(report["critical_changes"]),
                                           "files": report.get("files", [])})

        # 7) Deliver (only on execute) ---------------------------------- #
        if mode is ExecutionMode.EXECUTE:
            task = {"id": exec_ctx["id"], "description": request}
            res.delivery = delivery_mod.deliver(task, self.config, base=base, bus=self.bus,
                                                release_locks=False)

        # 8) Learn — emit pipeline.completed FIRST so the Self Improvement Engine
        #    consolidates the run into the Brain (synchronous bus), then read the
        #    post-learning Brain version.
        self.bus.emit("pipeline.completed", {"request": request})
        res.brain_version = self.brain.version()
        res.experience = self.experience.summary()
        self.experience.persist_summary()
        self.telemetry.export()
        return res

    # -- helpers --------------------------------------------------------- #
    def _exec_ctx(self, request: str, plan, selected: set[str]) -> dict[str, Any]:
        from nx_core.foundation import util
        subs = []
        for s in plan.subtasks:
            if s.agent in selected:
                deps = [d for d in s.depends_on if d in selected]
                subs.append({"agent": s.agent, "objective": s.objective,
                             "areas": s.areas, "depends_on": deps, "acceptance": s.acceptance})
        return {"id": util.task_id(request), "subtasks": subs}

    def _drive_modes(self, engine: ExecutionEngine, ctx: dict, mode: ExecutionMode) -> None:
        sequence = {
            ExecutionMode.DRY_RUN: [ExecutionMode.DRY_RUN],
            ExecutionMode.TEST: [ExecutionMode.DRY_RUN, ExecutionMode.TEST],
            ExecutionMode.EXECUTE: [ExecutionMode.DRY_RUN, ExecutionMode.TEST, ExecutionMode.EXECUTE],
        }[mode]
        for m in sequence:
            engine.run(ctx, m)
