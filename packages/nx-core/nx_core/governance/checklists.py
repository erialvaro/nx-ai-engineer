"""Checklists — per-stage/agent checklists fed into tasks and PRs."""
from __future__ import annotations

GLOBAL = [
    "Re-read PROJECT_RULES.md and the agent spec",
    "No forbidden/protected path touched",
    "Tests added/updated and passing",
    "Change documented",
]

PER_AGENT = {
    "database": ["Migration reversible", "No data loss", "Indexes considered"],
    "security": ["Authorization enforced", "Input validated", "No secret leakage"],
    "backend": ["No breaking API change", "Errors handled", "Logs preserved"],
    "frontend": ["No console errors", "Accessible", "Loading/empty/error states"],
    "qa": ["Edge cases covered", "Deterministic", "Full suite run"],
    "delivery": ["Reviewer approved", "Rollback documented", "Locks released"],
}


def for_agent(agent: str) -> list[str]:
    return [*GLOBAL, *PER_AGENT.get(agent, [])]
