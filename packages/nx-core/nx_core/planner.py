"""Planner Engine + Dependency Engine.

Given a free-text goal and the architecture memory, produce a structured plan:
which agents are involved, candidate files/areas, subtask ordering, risks,
priority and acceptance criteria. This is heuristic, deterministic and offline
— it produces a *scaffold* for the AI agents to execute, never the code itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import agents as agents_mod
from .agents import CANON_ORDER as _ORDER  # single source of truth (see agents.py)

# Dependency edges: agent -> agents whose work it relies on.
_DEPENDS_ON = {
    "backend": ["database", "security", "architect"],
    "ai": ["backend"],
    "frontend": ["backend"],
    "devops": ["backend", "database"],
    "qa": ["backend", "frontend", "ai", "database", "security"],
    "reviewer": ["backend", "frontend", "ai", "database", "security", "devops", "qa"],
    "delivery": ["reviewer"],
    "docs": ["delivery"],
}

# Words that escalate priority.
_HIGH_SIGNALS = ["auth", "payment", "billing", "security", "migration", "delete", "encrypt", "tenant", "pii"]


@dataclass
class Subtask:
    agent: str
    objective: str
    areas: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)


@dataclass
class Plan:
    description: str
    priority: str
    involved_agents: list[str]
    subtasks: list[Subtask]
    risks: list[str]
    acceptance: list[str]


def _match_agents(description: str, reg: dict[str, agents_mod.Agent]) -> list[str]:
    text = description.lower()
    scored: list[tuple[int, str]] = []
    for agent in reg.values():
        score = sum(1 for kw in agent.keywords if kw in text)
        if score:
            scored.append((score, agent.name))
    involved = {name for _, name in scored}

    # Sensible defaults: most features touch backend; always QA + review.
    if not involved:
        involved.add("backend")
    # Security/AI/data work almost always needs server wiring too.
    if involved & {"security", "ai", "database"}:
        involved.add("backend")
    involved.update({"qa", "reviewer", "delivery"})
    # Architect joins anything structural or multi-agent.
    if len(involved - {"qa", "reviewer", "delivery"}) > 1 or "architect" in involved:
        involved.add("architect")
    return [a for a in _ORDER if a in involved]


def _candidate_areas(agent: str, arch: dict[str, Any], reg: dict[str, agents_mod.Agent]) -> list[str]:
    """Map an agent to concrete top-level dirs that look like its territory."""
    spec = reg.get(agent)
    if not spec or spec.read_only:
        return []
    dirs = arch.get("top_level_dirs", []) + arch.get("workspaces", [])
    areas = []
    for d in dirs:
        probe = f"{d.rstrip('/*')}/x"
        if spec.owns(probe) or any(
            tok in d.lower() for tok in _territory_tokens(agent)
        ):
            areas.append(d)
    return sorted(set(areas))[:8]


def _territory_tokens(agent: str) -> list[str]:
    return {
        "backend": ["api", "server", "backend", "service"],
        "frontend": ["web", "frontend", "client", "ui", "app"],
        "database": ["db", "database", "migration", "model", "schema"],
        "ai": ["ai", "ml", "rag", "prompt", "llm"],
        "security": ["auth", "security"],
        "devops": ["docker", "infra", "ci", "deploy", "ops"],
        "qa": ["test", "tests", "e2e"],
        "docs": ["docs", "doc"],
    }.get(agent, [])


def _acceptance_for(agent: str, config: dict[str, Any]) -> list[str]:
    base = {
        "database": ["Migration is reversible", "No data loss", "Indexes considered"],
        "backend": ["No breaking API changes", "Errors handled", "Logging preserved"],
        "frontend": ["No console errors", "Responsive", "Accessible labels"],
        "ai": ["Prompts versioned", "Token/cost considered", "Deterministic where required"],
        "security": ["Input validated", "No secret leakage", "Least privilege"],
        "devops": ["Pipeline green", "Rollback documented", "No new infra drift"],
        "qa": ["New tests added", "Existing tests pass", "Edge cases covered"],
    }.get(agent, ["Existing tests pass", "Change documented"])
    rules = config.get("domain_rules") or []
    if agent in ("backend", "database", "security") and rules:
        base.append("Domain invariants preserved: " + "; ".join(rules))
    return base


def build_plan(description: str, arch: dict[str, Any], config: dict[str, Any]) -> Plan:
    reg = agents_mod.registry(config)
    involved = _match_agents(description, reg)

    text = description.lower()
    priority = "high" if any(s in text for s in _HIGH_SIGNALS) else "normal"

    subtasks: list[Subtask] = []
    for agent in involved:
        deps = [d for d in _DEPENDS_ON.get(agent, []) if d in involved]
        subtasks.append(Subtask(
            agent=agent,
            objective=_objective_for(agent, description),
            areas=_candidate_areas(agent, arch, reg),
            depends_on=deps,
            acceptance=_acceptance_for(agent, config),
        ))

    risks = _risks(description, arch, config, involved)
    acceptance = [
        "All existing tests pass; new behavior is covered by tests.",
        "No existing functionality is broken or removed.",
        "Change is documented and follows existing patterns.",
    ]
    if config.get("domain_rules"):
        acceptance.append("Domain invariants preserved: " + "; ".join(config["domain_rules"]))

    return Plan(description, priority, involved, subtasks, risks, acceptance)


def _objective_for(agent: str, description: str) -> str:
    verb = {
        "architect": "Define boundaries and design approach for",
        "database": "Model/migrate data required for",
        "security": "Secure authn/authz & validation for",
        "backend": "Implement server-side logic for",
        "ai": "Implement prompts/RAG/model logic for",
        "frontend": "Build the UI for",
        "devops": "Wire CI/CD & infra for",
        "qa": "Write and run tests for",
        "reviewer": "Review the full diff for",
        "delivery": "Consolidate and package",
        "docs": "Document",
    }.get(agent, "Work on")
    return f"{verb}: {description}"


def _risks(description: str, arch: dict[str, Any], config: dict[str, Any], involved: list[str]) -> list[str]:
    risks: list[str] = []
    text = description.lower()
    if "database" in involved:
        risks.append("Schema change — guard against data loss and downtime.")
    if "security" in involved or any(s in text for s in ["auth", "oauth", "token", "permission"]):
        risks.append("Security-sensitive — require tests and a security review.")
    if not arch.get("has_tests"):
        risks.append("Project lacks tests — add coverage before/with this change.")
    if arch.get("is_monorepo"):
        risks.append("Monorepo — verify no unintended cross-workspace impact.")
    for rule in config.get("domain_rules", []):
        risks.append(f"Must not violate: {rule}")
    return risks


# --------------------------------------------------------------------------- #
# Dependency Engine: topological order of the subtasks.
# --------------------------------------------------------------------------- #
def execution_order(plan: Plan) -> list[str]:
    names = [s.agent for s in plan.subtasks]
    dep = {s.agent: [d for d in s.depends_on if d in names] for s in plan.subtasks}
    ordered: list[str] = []
    visiting: set[str] = set()

    def visit(n: str) -> None:
        if n in ordered or n not in dep:
            return
        if n in visiting:  # cycle guard
            return
        visiting.add(n)
        for d in dep[n]:
            visit(d)
        visiting.discard(n)
        if n not in ordered:
            ordered.append(n)

    for n in sorted(names, key=lambda x: _ORDER.index(x) if x in _ORDER else 99):
        visit(n)
    return ordered
