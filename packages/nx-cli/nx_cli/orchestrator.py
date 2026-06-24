#!/usr/bin/env python
"""AIES Orchestrator — the single CLI entrypoint for the AI Engineering System.

Usage:
  python orchestrator.py audit                 Discover the architecture (run first).
  python orchestrator.py plan "<goal>"         Audit (cached) + plan + create a task.
  python orchestrator.py review [--base REF]    Consolidated diff review report.
  python orchestrator.py worktree <agent|--plan TASK>
                                                Create isolated git worktree lane(s).
  python orchestrator.py tasks                  List known tasks.
  python orchestrator.py locks                  Show active file locks.
  python orchestrator.py unlock --task ID       Release a task's locks.
  python orchestrator.py status                 One-shot overview.

Design: this file is thin glue. All logic lives in the nx_* engine packages, each
single-responsibility, so new commands/engines slot in without rewrites.
The mandatory workflow (audit before anything) is enforced here: `plan`
refuses to run until an architecture memory exists (and builds it if missing).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Windows consoles default to cp1252; force UTF-8 so reports render cleanly.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

from nx_core import analyzer, config as config_mod, locks as locks_mod  # noqa: E402
from nx_core import planner, review as review_mod, tasks as tasks_mod  # noqa: E402
from nx_core import util, worktree  # noqa: E402
from nx_core.kernel.engine import ExecutionMode  # noqa: E402
from nx_core.observability.events import EventBus  # noqa: E402
from nx_runtime.schedulers.dispatcher import AgentDispatcher  # noqa: E402
from nx_runtime.schedulers.execution import ExecutionEngine, ExecutionPolicy  # noqa: E402


def _cfg() -> dict:
    return config_mod.load()


def _make_adapter(name: str):
    """Resolve an adapter by name. 'dry-run' (default) is always safe; 'claude-code'
    runs real work via the Claude Code CLI; other names come from the SDK registry."""
    if name in (None, "dry-run", "dryrun"):
        from nx_runtime.adapters.dryrun import DryRunAdapter
        return DryRunAdapter()
    if name in ("claude-code", "claude"):
        from nx_runtime.adapters.claude_code import ClaudeCodeAdapter
        if not ClaudeCodeAdapter.available():
            util.eprint("warning: 'claude' CLI not found on PATH — execute will fail "
                        "until configured. Proceeding (dry/test stay safe).")
        return ClaudeCodeAdapter()
    import nx_sdk as sdk
    adapter = sdk.get_adapter(name)
    if adapter is None:
        util.eprint(f"error: unknown adapter '{name}'. Use dry-run, claude-code, "
                    f"or an SDK-registered name.")
        raise SystemExit(2)
    return adapter


def cmd_audit(_: argparse.Namespace) -> int:
    cfg = _cfg()
    print(util.banner(f"AUDIT — {cfg['project_name']}"))
    result = analyzer.run_and_persist(config=cfg)
    arch, aud = result["architecture"], result["audit"]
    print(f"\nStack:      {aud['summary']}")
    print(f"Files:      {arch['scanned_files']} scanned")
    print(f"Languages:  {', '.join(f'{k}({v})' for k, v in list(arch['languages'].items())[:6]) or '—'}")
    print(f"Monorepo:   {arch['is_monorepo']}  |  Tests: {arch['has_tests']}  |  Docker: {arch['has_docker']}")
    print(f"CI:         {', '.join(arch['ci']) or '—'}")
    print("\nStrengths:")
    for s in aud["strengths"]:
        print(f"  + {s}")
    print("\nRisks:")
    for r in aud["risks"]:
        print(f"  ! {r}")
    print(f"\nMemory written to {util.rel(util.config_root() / 'memory')}/")
    return 0


def _ensure_memory(cfg: dict) -> dict:
    mem = analyzer.load_memory()
    if not mem["architecture"]:
        print("[audit] No architecture memory found — running audit first…\n")
        analyzer.run_and_persist(config=cfg)
        mem = analyzer.load_memory()
    return mem


def cmd_plan(args: argparse.Namespace) -> int:
    description = args.goal.strip()
    if not description:
        util.eprint("error: provide a goal, e.g. plan \"Add OAuth login\"")
        return 2
    cfg = _cfg()
    mem = _ensure_memory(cfg)
    arch = mem["architecture"]

    plan = planner.build_plan(description, arch, cfg)
    tid = util.task_id(description)
    result = tasks_mod.create(plan, tid)

    print(util.banner(f"PLAN — {tid}"))
    print(f"\nGoal:     {description}")
    print(f"Priority: {plan.priority}")
    print(f"Agents:   {', '.join(plan.involved_agents)}")
    print(f"Order:    {' -> '.join(planner.execution_order(plan))}")
    print("\nSubtasks:")
    for s in plan.subtasks:
        areas = ", ".join(s.areas) or "—"
        deps = ", ".join(s.depends_on) or "—"
        print(f"  [{s.agent}] areas: {areas}  (deps: {deps})")
    print("\nRisks:")
    for r in plan.risks or ["(none flagged — verify manually)"]:
        print(f"  ! {r}")
    if result["conflicts"]:
        print("\n⚠️  Lock conflicts:")
        for c in result["conflicts"]:
            print(f"  - {c.get('requested')} held by task {c.get('task')} ({c.get('owner')})")
    print(f"\nTask written: {util.rel(Path(result['path']))}")
    print(f"Locked areas: {', '.join(result['locked']) or '—'}")
    print("\nNext: open the task file, dispatch each agent in order, then `review`.")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    cfg = _cfg()
    base = args.base or cfg.get("default_base", "HEAD")
    out = review_mod.run_and_persist(base, cfg)
    print(out["markdown"])
    print(f"\n_Report saved to {util.rel(Path(out['path']))}_")
    return 0


def cmd_obsidian(args: argparse.Namespace) -> int:
    """Sync the Obsidian vault from the Project Brain, or show its status."""
    from nx_obsidian.knowledge.obsidian_sync import ObsidianSync
    from nx_knowledge.memory.brain import ProjectBrain
    sync = ObsidianSync(ProjectBrain(), config=_cfg())
    if args.action == "sync":
        report = sync.sync()
        print(util.banner("OBSIDIAN SYNC"))
        print(f"\nVault:     {report['vault']}")
        print(f"Notes:     {report['total']} (written {report['written']}, "
              f"unchanged {report['unchanged']}, removed {report['removed']})")
        print("Incremental: only changed notes were rewritten.")
        return 0
    # status
    manifest = util.read_json(Path(sync.vault) / ".aies-sync.json", {}) or {}
    print(util.banner("OBSIDIAN STATUS"))
    print(f"\nVault:        {sync.vault}")
    print(f"Exists:       {Path(sync.vault).exists()}")
    print(f"Notes:        {manifest.get('count', 0)}")
    print(f"Brain ver:    {manifest.get('brain_version', '?')}")
    print(f"Last synced:  {manifest.get('synced_at', 'never')}")
    return 0


def cmd_knowledge(args: argparse.Namespace) -> int:
    """Knowledge Engine + Providers: index / list / retrieve / sync / status.

    sync/status coordinate the three memories (Brain=operational,
    Obsidian=organizational, Git=historical)."""
    from nx_knowledge.knowledge.engine import KnowledgeEngine
    from nx_knowledge.knowledge.registry import default_registry
    from nx_knowledge.memory.brain import ProjectBrain
    cfg = _cfg()

    if args.action in ("sync", "status", "graph"):
        engine = KnowledgeEngine(ProjectBrain(), config=cfg)
        if args.action == "graph":
            g = engine.graph()
            if args.format == "mermaid":
                print(g.to_mermaid())
            elif args.format == "json":
                import json
                print(json.dumps(g.as_dict(), ensure_ascii=False, indent=2))
            else:
                print(util.banner("KNOWLEDGE GRAPH"))
                print(f"\n{g.stats()}")
                if args.query:
                    rel = engine.enrich_context([args.query])
                    print(f"\nRelated to '{args.query}':")
                    for t, items in sorted(rel.items()):
                        print(f"  {t}: {', '.join(items[:8])}")
            return 0
        if args.action == "sync":
            rep = engine.sync(commit=args.commit)
            print(util.banner("KNOWLEDGE SYNC — three memories"))
            print(f"\n  Operational  (Project Brain): v{rep['operational']['version']}")
            print(f"  Organizational (Obsidian):    {rep['organizational']['notes']} notes "
                  f"(written {rep['organizational']['written']})")
            print(f"  Historical    (Git):          head {rep['historical']['head']}"
                  f"{'  [committed]' if rep['historical']['committed'] else ''}")
            return 0
        st = engine.status()
        print(util.banner("KNOWLEDGE STATUS — three memories"))
        print(f"\n  Operational    (Project Brain): v{st['operational']['version']}")
        org = st["organizational"]
        print(f"  Organizational (Obsidian):      {org['notes']} notes @ brain v{org['brain_version']} "
              f"({'in sync' if org['in_sync'] else 'STALE'})")
        his = st["historical"]
        print(f"  Historical     (Git):           repo={his['is_repo']} head={his['head']} "
              f"commits={his['commits']}")
        rich = st.get("richness", {})
        print(f"\n  Context richness: {rich.get('nodes', 0)} elements, "
              f"{rich.get('edges', 0)} relationships (grows with history → fewer tokens)")
        print(f"  Synchronized: {'YES' if st['synchronized'] else 'NO'}")
        return 0

    reg = default_registry(config=cfg, brain=ProjectBrain())

    if args.action == "index":
        counts = reg.index_all()
        print(util.banner("KNOWLEDGE INDEX"))
        for name, n in counts.items():
            print(f"  {name:<14} {n} item(s)")
        return 0

    if args.action == "list":
        provider = reg.get(args.provider) if args.provider else None
        items = provider.catalog() if provider else reg.catalog()
        print(util.banner(f"KNOWLEDGE — {args.provider or 'all'} ({len(items)})"))
        for it in items[: args.limit]:
            rels = f"  ->{len(it.relationships)} rel" if it.relationships else ""
            print(f"  [{it.provider}/{it.kind}] {it.ref}  «{it.title[:40]}»{rels}")
        return 0

    if args.action == "retrieve":
        providers = [args.provider] if args.provider else None
        items = reg.retrieve({"query": args.query or "", "limit": args.limit}, providers=providers)
        print(util.banner(f"RETRIEVE — '{args.query}'"))
        for it in items[: args.limit]:
            print(f"  [{it.provider}/{it.kind}] {it.ref}  «{it.title[:40]}»")
        return 0
    return 2


def cmd_insights(_: argparse.Namespace) -> int:
    """Show what the platform has learned (Experience Analyzer + Pattern Discovery)."""
    from nx_knowledge.evolution import SelfImprovementEngine
    ins = SelfImprovementEngine().insights()
    exp = ins["experience"]
    print(util.banner("INSIGHTS"))
    if exp.get("runs", 0) == 0:
        print("\nNo learning yet. Run `pipeline` to teach the platform.")
        return 0
    print(f"\nRuns learned:   {exp['runs']}  (Brain v{ins['brain_version']})")
    print(f"Success rate:   {exp['success_rate']}")
    print(f"Rework rate:    {exp['rework_rate']}")
    print(f"Avg duration:   {exp['avg_duration_sec']} s")
    print(f"Agent freq:     {exp['agent_frequency']}")
    print(f"Workflow succ:  {exp['workflow_success']}")
    print(f"Risk dist:      {exp['risk_distribution']}")
    sets = (ins["patterns"]["recurring_agent_sets"] or {}).get("sets")
    if sets:
        print("\nRecurring agent sets:")
        for s in sets:
            print(f"   - {s['agents']} (x{s['count']})")
    know = ins.get("knowledge") or {}
    if know:
        print("\nStructured knowledge (accrued by Project Evolution):")
        print("   " + " · ".join(f"{k}={v}" for k, v in know.items()))
    return 0


def cmd_recommend(args: argparse.Namespace) -> int:
    """Recommend how to approach a goal based on what worked before."""
    from nx_knowledge.evolution import SelfImprovementEngine
    rec = SelfImprovementEngine().recommendations(args.goal)
    print(util.banner("RECOMMENDATION"))
    print(f"\nGoal: {args.goal}")
    print(f"Based on {rec['based_on_runs']} learned run(s).")
    print(f"Recommended workflow: {rec['recommended_workflow']}")
    print(f"Recommended agents:   {', '.join(rec['recommended_agents']) or '—'}")
    if rec["similar_tasks"]:
        print("\nSimilar past tasks:")
        for s in rec["similar_tasks"]:
            print(f"   - {s['request_id']} (score {s['score']}) wf={s['workflow']} status={s['status']}")
    if rec["warnings"]:
        print("\nWarnings:")
        for w in rec["warnings"]:
            print(f"   ! {w}")
    return 0


def cmd_metrics(_: argparse.Namespace) -> int:
    """Show the latest persisted KPIs (Experience) and telemetry snapshot."""
    root = util.config_root()
    exp = util.read_json(root / "experience" / "summary.json", {}) or {}
    tel = util.read_json(root / "metrics" / "telemetry.json", {}) or {}
    print(util.banner("METRICS"))
    if not exp and not tel:
        print("\nNo metrics yet. Run `pipeline` first.")
        return 0
    print("\nExperience (KPIs over time):")
    for k, v in exp.items():
        print(f"  {k}: {v}")
    if tel.get("kpis"):
        print("\nTelemetry (last run snapshot):")
        for k, v in tel["kpis"].items():
            print(f"  {k}: {v}")
        print(f"  events_total: {tel.get('events_total')}")
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    """Run the full end-to-end pipeline for a goal (safe by default: dry_run)."""
    from nx_runtime.kernel.pipeline import Pipeline
    mode = ExecutionMode(args.mode)
    adapter = _make_adapter(args.adapter)
    res = Pipeline(adapter=adapter, record_adr=args.adr,
                   max_workers=args.workers).run(args.goal, mode=mode, base=args.base or "HEAD")
    print(util.banner(f"PIPELINE [{mode.value}]"))
    print(f"\nGoal:         {res.request}")
    print(f"Architecture: {res.architecture}")
    print(f"Selected:     {', '.join(res.selected_agents)}")
    print(f"Skipped:      {', '.join(res.skipped_agents)}")
    if res.context_reduction:
        avg = sum(res.context_reduction.values()) / len(res.context_reduction)
        print(f"Context:      avg reduction {avg*100:.1f}% across {len(res.context_reduction)} agents")
    print(f"Execution:    {res.execution.get('status')} — {res.execution.get('metrics')}")
    print(f"Review:       {res.review.get('total_changed')} changed, "
          f"{res.review.get('without_tests')} without tests, {res.review.get('critical')} critical")
    if res.delivery:
        print(f"Delivery:     gates {'PASSED' if res.delivery.get('gates_passed') else 'BLOCKED'}")
    print(f"Brain:        v{res.brain_version}")
    print(f"Experience:   {res.experience}")
    return 0


def cmd_deliver(args: argparse.Namespace) -> int:
    """Consolidate a reviewed task into a PR; gate-check and release locks."""
    from nx_runtime.engines import delivery
    data = tasks_mod.load(args.plan)
    if not data:
        util.eprint(f"error: task {args.plan} not found")
        return 2
    cfg = _cfg()
    bus = EventBus()
    res = delivery.deliver(data, cfg, base=args.base or cfg.get("default_base", "HEAD"), bus=bus)
    print(util.banner(f"DELIVER — {res['task']}"))
    print(f"\nQuality gates: {'PASSED' if res['gates_passed'] else 'BLOCKED'}")
    if res["blocking"]:
        print(f"  Blocking: {', '.join(res['blocking'])}")
    print(f"PR written:    {util.rel(Path(res['pr_path']))}")
    print(f"Locks released: {res['locks_released']}")
    print(f"Rollback:      {res['rollback']}")
    return 0 if res["gates_passed"] else 1


def cmd_context(args: argparse.Namespace) -> int:
    """Build the minimal context for one agent of a planned task."""
    from nx_core.kernel.domain import Subtask
    from nx_knowledge.memory.context import ContextBuilder

    data = tasks_mod.load(args.plan)
    if not data:
        util.eprint(f"error: task {args.plan} not found")
        return 2
    raw = next((s for s in data.get("subtasks", []) if s.get("agent") == args.agent), None)
    if not raw:
        util.eprint(f"error: agent '{args.agent}' is not part of task {args.plan}")
        return 2

    sub = Subtask(id=raw["agent"], agent=raw["agent"], objective=raw.get("objective", ""),
                  areas=raw.get("areas", []), acceptance=raw.get("acceptance", []))
    mem = analyzer.load_memory()
    res = ContextBuilder().build(agent=args.agent, subtask=sub,
                                 config=_cfg(), arch=mem.get("architecture", {}),
                                 use_cache=not args.no_cache)
    c = res.context
    print(util.banner(f"CONTEXT — {args.agent} @ {data['id']}"))
    print(f"\nReduction: {res.estimated_reduction*100:.1f}% "
          f"({res.included_files}/{res.total_files} files included){'  [cached]' if res.cached else ''}")
    for label, items in (("files", c.files), ("services", c.services), ("apis", c.apis),
                         ("tests", c.tests), ("docs", c.docs), ("patterns", c.patterns)):
        if items:
            print(f"\n{label}:")
            for it in items:
                print(f"  - {it}")
    return 0


def cmd_decide(args: argparse.Namespace) -> int:
    """Make the full execution decision for a goal (agents, workflow, order,
    risk, impact, cost, time, review/QA, parallelism)."""
    from nx_runtime.intelligence.decision import DecisionEngine
    cfg = _cfg()
    arch = analyzer.load_memory().get("architecture", {})
    bus = EventBus()
    d = DecisionEngine(bus=bus).decide(args.goal, arch=arch, config=cfg, record_adr=args.adr)

    print(util.banner("DECISION"))
    print(f"\nGoal:        {d.request}")
    print(f"Workflow:    {d.workflow}")
    print(f"Agents:      {', '.join(d.agents)}")
    print(f"Skipped:     {', '.join(d.skipped)}")
    print(f"Order:       {' -> '.join(d.execution_order)}")
    print(f"Parallelism: {d.parallelism} ({'yes' if d.parallelizable else 'no'})  "
          f"layers={d.parallel_layers}")
    print(f"Risk:        {d.risk_level}")
    for r in d.risks[:6]:
        print(f"   - {r}")
    print(f"Impact:      {d.impact}")
    print(f"Est. cost:   ~{d.estimated_cost_tokens} tokens")
    print(f"Est. time:   ~{d.estimated_time_min} min (parallel)")
    print(f"Review:      {'required' if d.needs_review else 'light'}")
    print(f"QA:          {'required' if d.needs_qa else 'optional'}")
    print(f"Confidence:  {d.confidence}")
    print("\nRationale:")
    for line in d.rationale:
        print(f"   - {line}")
    return 0


def cmd_dispatch(args: argparse.Namespace) -> int:
    """Select only the agents a goal needs (and show what is skipped + why)."""
    cfg = _cfg()
    if args.plan:
        data = tasks_mod.load(args.plan)
        if not data:
            util.eprint(f"error: task {args.plan} not found")
            return 2
        description = data["description"]
    elif args.goal:
        description = args.goal
    else:
        util.eprint("error: pass a goal or --plan <task-id>")
        return 2

    dispatcher = AgentDispatcher()
    selections = dispatcher.dispatch(description=description, config=cfg)
    chosen = AgentDispatcher.selected(selections)

    print(util.banner("DISPATCH"))
    print(f"\nGoal: {description}")
    print(f"Strategy: {dispatcher.strategy_name}")
    print(f"\nSelected ({len(chosen)}):")
    for s in chosen:
        deps = f"  (deps: {', '.join(s.depends_on)})" if s.depends_on else ""
        print(f"  {s.order:>2}. {s.agent:<10} — {s.reason}{deps}")
    skipped = [s for s in selections if not s.selected]
    print(f"\nSkipped ({len(skipped)}): " + ", ".join(s.agent for s in skipped))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Execute a planned task's subtasks through the Execution Engine.

    Modes follow the mandatory Dry Run -> Test -> Execute progression. Even
    'execute' is safe by default: it uses the DryRunAdapter (no code is changed)
    until a real adapter is wired in. The mode gate is enforced by the engine.
    """
    data = tasks_mod.load(args.plan)
    if not data:
        util.eprint(f"error: task {args.plan} not found")
        return 2

    mode = ExecutionMode(args.mode)
    bus = EventBus()
    transitions: list[str] = []
    bus.subscribe("task.state_changed",
                  lambda e: transitions.append(f"{e.node_id}: {e.payload['from']}->{e.payload['to']}"))

    adapter = _make_adapter(args.adapter)
    if args.workers and args.workers > 1:
        from nx_runtime.schedulers.cluster import ClusterPolicy, ExecutionCluster
        engine = ExecutionCluster(
            bus=bus, adapter=adapter, lock_provider=locks_mod,
            policy=ClusterPolicy(max_workers=args.workers, max_retries=args.retries),
            persist=True,
        )
        engine_label = f"cluster x{args.workers}"
    else:
        engine = ExecutionEngine(
            bus=bus, adapter=adapter, lock_provider=locks_mod,
            policy=ExecutionPolicy(max_retries=args.retries), persist=True,
        )
        engine_label = "engine"

    print(util.banner(f"RUN — {data['id']} [{mode.value}] via {adapter.name} ({engine_label})"))
    # Enforce the gate: build up to the requested mode.
    sequence = {
        ExecutionMode.DRY_RUN: [ExecutionMode.DRY_RUN],
        ExecutionMode.TEST: [ExecutionMode.DRY_RUN, ExecutionMode.TEST],
        ExecutionMode.EXECUTE: [ExecutionMode.DRY_RUN, ExecutionMode.TEST, ExecutionMode.EXECUTE],
    }[mode]

    result = None
    for m in sequence:
        result = engine.run(data, m)
        print(f"\n[{m.value}] ok={result.ok}")
        for a in result.actions:
            print(f"   - {a['agent']:<10} {a['state']:<10} (attempts={a['attempts']})")
        if not result.ok and m is not mode:
            print(f"\nStopped: '{m.value}' did not pass; not advancing to '{mode.value}'.")
            break

    print(f"\nProgress: {engine.progress()}")
    if result and result.ok and mode is ExecutionMode.EXECUTE:
        print(f"Run persisted under {util.rel(util.config_root() / 'runs')}/")
    return 0


def cmd_worktree(args: argparse.Namespace) -> int:
    cfg = _cfg()
    if args.plan:
        data = tasks_mod.load(args.plan)
        if not data:
            util.eprint(f"error: task {args.plan} not found")
            return 2
        results = worktree.create_for_plan(data.get("agents", []), cfg)
    elif args.agent:
        results = [worktree.create(args.agent, cfg)]
    else:
        util.eprint("error: pass an <agent> or --plan <task-id>")
        return 2
    for r in results:
        mark = "✓" if r.get("ok") else "✗"
        print(f"  {mark} {r.get('branch', '?')}: {r['message']}")
    return 0


def cmd_tasks(_: argparse.Namespace) -> int:
    rows = tasks_mod.list_tasks()
    if not rows:
        print("No tasks yet. Create one with: plan \"<goal>\"")
        return 0
    print(util.banner("TASKS"))
    for t in rows:
        print(f"  [{t['status']:<8}] {t['id']}  ({t['priority']})  -> {', '.join(t['agents'])}")
    return 0


def cmd_locks(_: argparse.Namespace) -> int:
    active = locks_mod.active_locks()
    if not active:
        print("No active locks.")
        return 0
    print(util.banner("ACTIVE LOCKS"))
    for l in active:
        print(f"  {l['path']}  <- task {l['task']} ({l['owner']}) @ {l['acquired_at']}")
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    n = locks_mod.release(task=args.task, path=args.path)
    print(f"Released {n} lock(s).")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    cfg = _cfg()
    mem = analyzer.load_memory()
    print(util.banner(f"AIES STATUS — {cfg['project_name']}"))
    if mem["architecture"]:
        print(f"  Architecture: {mem['audit'].get('summary', '?')} "
              f"(audited {mem['architecture'].get('generated_at', '?')})")
    else:
        print("  Architecture: NOT AUDITED — run `audit` first.")
    print(f"  Tasks:  {len(tasks_mod.list_tasks())}")
    print(f"  Locks:  {len(locks_mod.active_locks())} active")
    wl = worktree.list_worktrees()
    print(f"  Worktrees: {max(0, len(wl) - 1)} extra lane(s)")
    return 0


def _version() -> str:
    import nx_core
    return getattr(nx_core, "__version__", "0.0.0")


def cmd_version(_: argparse.Namespace) -> int:
    print(f"nx-ai-engineer {_version()}")
    print(f"python {sys.version.split()[0]} on {sys.platform}")
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    """Show the project Knowledge Graph (top-level alias of `knowledge graph`)."""
    args.action = "graph"
    args.provider = getattr(args, "provider", None)
    args.limit = getattr(args, "limit", 20)
    args.commit = getattr(args, "commit", False)
    return cmd_knowledge(args)


def cmd_report(_: argparse.Namespace) -> int:
    """Consolidated project report: status + learning insights + KPIs/telemetry.

    A composition of existing read-only views — no new analysis."""
    ns = argparse.Namespace()
    cmd_status(ns)
    print()
    cmd_insights(ns)
    print()
    cmd_metrics(ns)
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a project: scaffold .ai-project-assistant (data only) from the bundled
    template, then audit -> Project Brain -> Knowledge Engine -> Obsidian vault."""
    from nx_cli import bootstrap
    target = Path(args.path).resolve()
    root, copied, skipped = bootstrap.init(target, force=args.force)
    print(util.banner(f"NXAI INIT — {target.name}"))
    print(f"\n  .ai-project-assistant: {root}")
    print(f"  template:    {copied} file(s) written, {skipped} kept")
    # Point the engines at the freshly created home.
    os.environ["AIES_HOME"] = str(root)
    if args.no_audit:
        print("\n  (skipped audit/brain/knowledge — run `nxai audit` when ready)")
    else:
        cfg = config_mod.load(root)
        try:
            print("\n  [1/3] audit ............ ", end="")
            analyzer.run_and_persist(config=cfg)
            print("ok")
        except Exception as exc:  # never let init crash on an odd project
            print(f"skipped ({exc.__class__.__name__})")
        try:
            print("  [2/3] knowledge + brain  ", end="")
            from nx_knowledge.knowledge.engine import KnowledgeEngine
            from nx_knowledge.memory.brain import ProjectBrain
            KnowledgeEngine(ProjectBrain(), config=cfg).sync()
            print("ok")
        except Exception as exc:
            print(f"skipped ({exc.__class__.__name__})")
        try:
            print("  [3/3] obsidian vault ... ", end="")
            from nx_obsidian.knowledge.obsidian_sync import ObsidianSync
            from nx_knowledge.memory.brain import ProjectBrain
            ObsidianSync(ProjectBrain(), config=cfg).sync()
            print("ok")
        except Exception as exc:
            print(f"skipped ({exc.__class__.__name__})")
    print("\n  Project initialized. Next:")
    print("    nxai audit            # (re)discover the architecture")
    print("    nxai plan \"<goal>\"     # plan a goal into a task")
    print("    nxai doctor           # verify the environment")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Refresh the template assets (framework/SDK/providers/templates) in an
    existing .ai-project-assistant. Never touches Brain/Vault/Knowledge/config/history."""
    from nx_cli import bootstrap
    target = Path(args.path).resolve()
    try:
        root, copied, skipped = bootstrap.update(target)
    except FileNotFoundError as exc:
        util.eprint(f"error: {exc}")
        return 2
    print(util.banner(f"NXAI UPDATE — {target.name}"))
    print(f"\n  .ai-project-assistant: {root}")
    print(f"  refreshed:   {copied} template file(s)")
    print("  preserved:   config.json, brain/, obsidian/, knowledge/, tasks/, history (untouched)")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    """Health-check the install + project (python, packages, template, project)."""
    from nx_cli import bootstrap
    checks: list[tuple[str, str, str]] = []

    def add(name, ok, detail, warn=False):
        checks.append((name, "PASS" if ok else ("WARN" if warn else "FAIL"), detail))

    add("python >= 3.8", sys.version_info[:2] >= (3, 8), sys.version.split()[0])
    vers = {}
    pkgs_ok = True
    for mod in ("nx_core", "nx_workflow", "nx_sdk", "nx_providers",
                "nx_obsidian", "nx_knowledge", "nx_runtime", "nx_cli"):
        try:
            m = __import__(mod)
            vers[mod] = getattr(m, "__version__", "?")
        except Exception:
            pkgs_ok = False
            vers[mod] = "MISSING"
    add("nx_* packages import", pkgs_ok, ", ".join(f"{k}={v}" for k, v in vers.items()))
    consistent = len({v for v in vers.values() if v not in ("?", "MISSING")}) <= 1
    add("package versions aligned", consistent, "all " + _version() if consistent else str(vers))
    tpl = bootstrap.template_dir()
    add("bundled template present", (tpl / "agents").is_dir(),
        f"{len(list((tpl / 'agents').glob('*.md')))} agent specs" if tpl.is_dir() else str(tpl))
    import shutil as _sh
    add("git available", bool(_sh.which("git")), _sh.which("git") or "not on PATH", warn=True)
    # project (.ai-project-assistant)
    try:
        root = util.config_root()
        has_proj = (root / "config.json").exists() or (root / "brain").is_dir()
    except Exception:
        root, has_proj = None, False
    if has_proj:
        add(".ai-project-assistant present", True, str(root))
        try:
            json.loads((root / "config.json").read_text(encoding="utf-8")) if (root / "config.json").exists() else {}
            add("config.json valid", True, "ok")
        except Exception as exc:
            add("config.json valid", False, str(exc))
        add(".ai-project-assistant writable", os.access(root, os.W_OK), "writable")
    else:
        add(".ai-project-assistant present", False, "run `nxai init` in your project", warn=True)

    print(util.banner("NXAI DOCTOR"))
    print()
    worst_ok = True
    for name, status, detail in checks:
        mark = {"PASS": "+", "WARN": "~", "FAIL": "x"}[status]
        print(f"  [{mark}] {name:28} {detail}")
        if status == "FAIL":
            worst_ok = False
    print(f"\n  {'All systems go.' if worst_ok else 'Problems found — see [x] above.'}")
    return 0 if worst_ok else 1


def cmd_docs(args: argparse.Namespace) -> int:
    """List the bundled guides, or print one (`nxai docs <name>`)."""
    from nx_cli import bootstrap
    docs_dir = bootstrap.template_dir() / "docs"
    if not docs_dir.is_dir():
        util.eprint("error: bundled docs not found")
        return 2
    files = sorted(docs_dir.glob("*.md")) + sorted(docs_dir.glob("adr/*.md"))
    if not args.name:
        print(util.banner("NXAI DOCS"))
        print(f"\n  {len(files)} document(s) in {docs_dir}:\n")
        for f in files:
            rel = f.relative_to(docs_dir)
            print(f"    {f.stem:34} ({rel})")
        print("\n  Read one with:  nxai docs <name>")
        return 0
    want = args.name.lower().replace(".md", "")
    match = next((f for f in files if f.stem.lower() == want), None)
    if match is None:
        match = next((f for f in files if want in f.stem.lower()), None)
    if match is None:
        util.eprint(f"error: no doc matching '{args.name}'. Run `nxai docs` to list.")
        return 2
    print(match.read_text(encoding="utf-8"))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    """Engineering Packs: list / show / add / remove domain knowledge bundles."""
    import nx_packs
    packs_root = util.config_root() / "packs"

    def installed() -> set:
        return {p.name for p in packs_root.iterdir()
                if (p / "pack.json").is_file()} if packs_root.is_dir() else set()

    if args.action == "list":
        have = installed()
        print(util.banner("ENGINEERING PACKS"))
        print()
        for m in nx_packs.catalog():
            mark = "[installed]" if m["name"] in have else "          "
            print(f"  {mark} {m['name']:16} {m.get('status',''):9} {m.get('summary','')[:60]}")
        extra = sorted(have - set(nx_packs.names()))
        for name in extra:
            print(f"  [installed] {name:16} (local)")
        print("\n  Add one with:  nxai pack add <name>")
        return 0

    if args.action == "show":
        if not args.name:
            util.eprint("error: `nxai pack show <name>` requires a pack name"); return 2
        try:
            m = nx_packs.manifest(args.name)
        except KeyError:
            util.eprint(f"error: unknown pack '{args.name}'. Run `nxai pack list`."); return 2
        print(util.banner(f"PACK — {m['title']}"))
        print(f"\n  name:    {m['name']}\n  domain:  {m['domain']}\n  status:  {m['status']}")
        print(f"  tags:    {', '.join(m.get('tags', []))}\n  summary: {m['summary']}")
        readme = nx_packs.pack_dir(args.name) / "README.md"
        if readme.is_file():
            print("\n" + readme.read_text(encoding="utf-8"))
        return 0

    if args.action == "add":
        if not args.name:
            util.eprint("error: `nxai pack add <name>` requires a pack name"); return 2
        try:
            dst = nx_packs.install(args.name, packs_root)
        except KeyError:
            util.eprint(f"error: unknown pack '{args.name}'. Run `nxai pack list`."); return 2
        print(util.banner(f"PACK ADDED — {args.name}"))
        print(f"\n  installed to: {dst}")
        print("  The Pack Provider now feeds its policies/checklists/context to agents.")
        return 0

    if args.action == "remove":
        if not args.name:
            util.eprint("error: `nxai pack remove <name>` requires a pack name"); return 2
        import shutil
        target = packs_root / args.name
        if not target.is_dir():
            util.eprint(f"error: pack '{args.name}' is not installed"); return 2
        shutil.rmtree(target)
        print(f"Removed pack '{args.name}' from {packs_root}.")
        return 0
    return 0


def _detect_stack() -> str:
    try:
        mem = analyzer.load_memory()
        langs = {str(k).lower() for k in (mem.get("architecture") or {}).get("languages", {})}
    except Exception:
        langs = set()
    if "python" in langs:
        return "python"
    if "typescript" in langs or "javascript" in langs:
        return "node"
    if "go" in langs:
        return "go"
    return "generic"


def cmd_scaffold(args: argparse.Namespace) -> int:
    """Lay open-source/GitHub repository standards (governance files, issue/PR
    templates, CI per stack) into the project root. Idempotent; never overwrites
    without --force. Sourced from the `repo-standards` pack."""
    import shutil
    import nx_packs
    root = Path(args.path).resolve() if args.path else util.project_root()
    try:
        scaffold = nx_packs.pack_dir("repo-standards") / "scaffold"
        manifest = json.loads((scaffold / "manifest.json").read_text(encoding="utf-8"))
    except Exception as exc:
        util.eprint(f"error: repo-standards scaffold unavailable ({exc})")
        return 2
    stack = args.stack if args.stack != "auto" else _detect_stack()
    if stack not in manifest.get("stacks", {}):
        stack = "generic"
    entries = list(manifest.get("common", [])) + list(manifest["stacks"].get(stack, []))
    print(util.banner(f"NXAI SCAFFOLD — {root.name}"))
    suffix = " (auto-detected)" if args.stack == "auto" else ""
    print(f"\n  target: {root}\n  stack:  {stack}{suffix}\n")
    written = skipped = 0
    for e in entries:
        src, dest = scaffold / e["src"], root / e["dest"]
        if not src.is_file():
            continue
        if dest.exists() and not args.force:
            print(f"    skip   {e['dest']} (exists)")
            skipped += 1
            continue
        if args.dry_run:
            print(f"    would write {e['dest']}")
            written += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"    write  {e['dest']}")
        written += 1
    verb = "would write" if args.dry_run else "wrote"
    print(f"\n  {verb} {written} file(s), skipped {skipped} existing.")
    if skipped and not args.force:
        print("  (use --force to overwrite existing files)")
    return 0


def cmd_contract(args: argparse.Namespace) -> int:
    """Build the Engineering Contract for an agent + task: the declarative brief
    (context/knowledge/engineering packs/constraints/requirements) the agent
    receives. Engineering Packs auto-attach by their `applies_to`."""
    from nx_knowledge.knowledge.engine import KnowledgeEngine
    from nx_knowledge.memory.brain import ProjectBrain
    cfg = _cfg()
    task = args.goal or ""
    files = list(args.files or [])
    areas = list(args.areas or [])
    if args.plan:
        data = tasks_mod.load(args.plan)
        if not data:
            util.eprint(f"error: task {args.plan} not found")
            return 2
        raw = next((s for s in data.get("subtasks", []) if s.get("agent") == args.agent), None)
        task = task or (raw.get("objective") if raw else "") or data.get("description") or data["id"]
        if raw:
            areas = areas or raw.get("areas", [])
            files = files or raw.get("files", [])
    if not task:
        util.eprint('error: provide a task — `nxai contract --agent <a> "<task>"` or --plan <id>')
        return 2
    contract = KnowledgeEngine(ProjectBrain(), config=cfg).build_contract(
        task, args.agent, files=files, areas=areas)
    if args.format == "json":
        print(json.dumps(contract.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(util.banner(f"ENGINEERING CONTRACT — {args.agent}"))
        print("\n" + contract.to_text())
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nxai",
                                description="NX AI Engineer — Developer Infrastructure Platform")
    p.add_argument("-V", "--version", action="version", version=f"nx-ai-engineer {_version()}")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="Initialize .ai-project-assistant (scaffold + audit + brain + vault)")
    sp.add_argument("path", nargs="?", default=".", help="Project dir (default: current)")
    sp.add_argument("--force", action="store_true", help="Overwrite existing template files")
    sp.add_argument("--no-audit", action="store_true", help="Scaffold only; skip audit/brain/vault")
    sp.set_defaults(fn=cmd_init)

    sp = sub.add_parser("update", help="Refresh template assets (keeps Brain/Vault/config/history)")
    sp.add_argument("path", nargs="?", default=".", help="Project dir (default: current)")
    sp.set_defaults(fn=cmd_update)

    sub.add_parser("doctor", help="Health-check the install and project").set_defaults(fn=cmd_doctor)

    sp = sub.add_parser("docs", help="List the bundled guides, or print one")
    sp.add_argument("name", nargs="?", help="Doc to print (e.g. SDK_GUIDE)")
    sp.set_defaults(fn=cmd_docs)

    sub.add_parser("version", help="Show version").set_defaults(fn=cmd_version)

    sp = sub.add_parser("graph", help="Show the project Knowledge Graph")
    sp.add_argument("--format", choices=["summary", "mermaid", "json"], default="summary")
    sp.add_argument("--query", help="A file path to show related elements for")
    sp.set_defaults(fn=cmd_graph)

    sub.add_parser("report", help="Consolidated report (status + insights + metrics)").set_defaults(fn=cmd_report)

    sp = sub.add_parser("pack", help="Engineering Packs (list/show/add/remove domain knowledge)")
    sp.add_argument("action", choices=["list", "show", "add", "remove"])
    sp.add_argument("name", nargs="?", help="Pack name (for show/add/remove)")
    sp.set_defaults(fn=cmd_pack)

    sp = sub.add_parser("scaffold", help="Lay open-source/GitHub repo standards into the project")
    sp.add_argument("target", nargs="?", default="github", choices=["github"],
                    help="What to scaffold (default: github)")
    sp.add_argument("--stack", default="auto",
                    choices=["auto", "python", "node", "go", "generic"],
                    help="Stack for the CI/.gitignore variant (default: auto-detect)")
    sp.add_argument("--force", action="store_true", help="Overwrite existing files")
    sp.add_argument("--dry-run", action="store_true", help="Show what would be written")
    sp.add_argument("--path", help="Project dir (default: the project root)")
    sp.set_defaults(fn=cmd_scaffold)

    sp = sub.add_parser("contract", help="Build the Engineering Contract for an agent + task")
    sp.add_argument("goal", nargs="?", help="Free-text task (or use --plan)")
    sp.add_argument("--agent", required=True, help="Agent the contract is for")
    sp.add_argument("--plan", help="Task id to derive task/areas from")
    sp.add_argument("--files", nargs="*", help="Files in scope")
    sp.add_argument("--areas", nargs="*", help="Areas in scope")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(fn=cmd_contract)

    sub.add_parser("audit", help="Discover & persist the project architecture").set_defaults(fn=cmd_audit)

    sp = sub.add_parser("plan", help="Plan a goal into a task")
    sp.add_argument("goal", help="Free-text development goal")
    sp.set_defaults(fn=cmd_plan)

    sp = sub.add_parser("review", help="Consolidated diff review")
    sp.add_argument("--base", default=None, help="Git ref to diff against (default: config)")
    sp.set_defaults(fn=cmd_review)

    sub.add_parser("metrics", help="Show persisted KPIs + telemetry").set_defaults(fn=cmd_metrics)
    sub.add_parser("insights", help="Show what the platform has learned").set_defaults(fn=cmd_insights)

    sp = sub.add_parser("knowledge",
                        help="Knowledge Engine + Providers (index/list/retrieve/sync/status/graph)")
    sp.add_argument("action", choices=["index", "list", "retrieve", "sync", "status", "graph"])
    sp.add_argument("--provider", help="Limit to one provider (filesystem/git/markdown/adr/project-brain/obsidian)")
    sp.add_argument("--query", help="Query for retrieve; or a file path for graph relations")
    sp.add_argument("--limit", type=int, default=20, help="Max items to show")
    sp.add_argument("--commit", action="store_true", help="On sync, snapshot to Git (historical memory)")
    sp.add_argument("--format", choices=["summary", "mermaid", "json"], default="summary",
                    help="graph output format")
    sp.set_defaults(fn=cmd_knowledge)

    sp = sub.add_parser("obsidian", help="Sync/inspect the Obsidian knowledge vault")
    sp.add_argument("action", choices=["sync", "status"])
    sp.set_defaults(fn=cmd_obsidian)

    sp = sub.add_parser("recommend", help="Recommend an approach from past learning")
    sp.add_argument("goal", help="Free-text development goal")
    sp.set_defaults(fn=cmd_recommend)

    sp = sub.add_parser("pipeline", help="Run the full end-to-end pipeline for a goal")
    sp.add_argument("goal", help="Free-text development goal")
    sp.add_argument("--mode", choices=["dry_run", "test", "execute"], default="dry_run")
    sp.add_argument("--adapter", default="dry-run",
                    help="Adapter: dry-run (default, safe) | claude-code | SDK name")
    sp.add_argument("--base", default=None, help="Diff base for review")
    sp.add_argument("--adr", action="store_true", help="Auto-generate ADRs from decisions")
    sp.add_argument("--workers", type=int, default=1,
                    help="Worker count: 1 = sequential (default); >1 = Execution Cluster")
    sp.set_defaults(fn=cmd_pipeline)

    # `execute` is the user-facing alias of the full end-to-end pipeline.
    sp = sub.add_parser("execute", help="Run the full end-to-end flow for a goal (alias of pipeline)")
    sp.add_argument("goal", help="Free-text development goal")
    sp.add_argument("--mode", choices=["dry_run", "test", "execute"], default="dry_run")
    sp.add_argument("--adapter", default="dry-run",
                    help="Adapter: dry-run (default, safe) | claude-code | SDK name")
    sp.add_argument("--base", default=None, help="Diff base for review")
    sp.add_argument("--adr", action="store_true", help="Auto-generate ADRs from decisions")
    sp.add_argument("--workers", type=int, default=1,
                    help="Worker count: 1 = sequential (default); >1 = Execution Cluster")
    sp.set_defaults(fn=cmd_pipeline)

    sp = sub.add_parser("deliver", help="Consolidate a task into a PR (gate-check + release locks)")
    sp.add_argument("--plan", required=True, help="Task id to deliver")
    sp.add_argument("--base", default=None, help="Diff base (default: config)")
    sp.set_defaults(fn=cmd_deliver)

    sp = sub.add_parser("context", help="Build minimal context for an agent of a task")
    sp.add_argument("--plan", required=True, help="Task id")
    sp.add_argument("--agent", required=True, help="Agent to build context for")
    sp.add_argument("--no-cache", action="store_true", help="Bypass the context cache")
    sp.set_defaults(fn=cmd_context)

    sp = sub.add_parser("decide", help="Full execution decision (Decision Engine)")
    sp.add_argument("goal", help="Free-text development goal")
    sp.add_argument("--adr", action="store_true", help="Record the decision as an ADR")
    sp.set_defaults(fn=cmd_decide)

    sp = sub.add_parser("dispatch", help="Select the agents a goal needs (Strategy)")
    sp.add_argument("goal", nargs="?", help="Free-text goal")
    sp.add_argument("--plan", help="Use a task id's description instead")
    sp.set_defaults(fn=cmd_dispatch)

    sp = sub.add_parser("run", help="Execute a planned task (Dry Run -> Test -> Execute)")
    sp.add_argument("--plan", required=True, help="Task id to execute")
    sp.add_argument("--mode", choices=["dry_run", "test", "execute"], default="dry_run",
                    help="Execution mode (default: dry_run; safe by default)")
    sp.add_argument("--adapter", default="dry-run",
                    help="Adapter: dry-run (default, safe) | claude-code | SDK name")
    sp.add_argument("--retries", type=int, default=1, help="Max retries per node")
    sp.add_argument("--workers", type=int, default=1,
                    help="Worker count: 1 = sequential engine (default); >1 = Execution Cluster")
    sp.set_defaults(fn=cmd_run)

    sp = sub.add_parser("worktree", help="Create isolated git worktree lanes")
    sp.add_argument("agent", nargs="?", help="Single agent lane to create")
    sp.add_argument("--plan", help="Create lanes for every agent in a task id")
    sp.set_defaults(fn=cmd_worktree)

    sub.add_parser("tasks", help="List tasks").set_defaults(fn=cmd_tasks)
    sub.add_parser("locks", help="List active locks").set_defaults(fn=cmd_locks)

    sp = sub.add_parser("unlock", help="Release locks")
    sp.add_argument("--task", help="Release all locks for this task id")
    sp.add_argument("--path", help="Release locks for this path")
    sp.set_defaults(fn=cmd_unlock)

    sub.add_parser("status", help="Overview").set_defaults(fn=cmd_status)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
