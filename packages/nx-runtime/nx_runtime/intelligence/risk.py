"""Intelligence · Risk analysis.

Classifies the risk of a goal/plan from the description, the discovered
architecture and the project's domain rules. Pure, deterministic, offline —
output feeds prioritization, Governance gates and the planner's risk list.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# token -> (severity, message)
_SIGNALS = {
    "auth": ("high", "Authentication/authorization change — require tests + security review."),
    "oauth": ("high", "OAuth flow — token handling and redirect safety."),
    "token": ("high", "Token/secret handling — never log; least privilege."),
    "password": ("high", "Credential handling — hashing and storage scrutiny."),
    "payment": ("high", "Payment path — correctness and idempotency critical."),
    "billing": ("high", "Billing change — financial impact; require approval."),
    "migration": ("high", "Schema migration — guard against data loss/downtime."),
    "delete": ("medium", "Deletion logic — verify scope and soft-delete needs."),
    "tenant": ("high", "Multi-tenant boundary — enforce isolation."),
    "pii": ("high", "Personal data — privacy/LGPD handling required."),
    "encrypt": ("medium", "Cryptography — use vetted primitives, no DIY."),
    "cache": ("low", "Caching — watch invalidation and per-tenant keys."),
    "concurren": ("medium", "Concurrency — race conditions and locking."),
}

_SEV_WEIGHT = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Risk:
    severity: str
    message: str
    source: str


def analyze(description: str, arch: dict[str, Any] | None = None,
            config: dict[str, Any] | None = None) -> list[Risk]:
    arch = arch or {}
    config = config or {}
    text = (description or "").lower()
    risks: list[Risk] = []

    for token, (sev, msg) in _SIGNALS.items():
        if token in text:
            risks.append(Risk(sev, msg, f"keyword:{token}"))

    if not arch.get("has_tests", True):
        risks.append(Risk("high", "Project lacks tests — add coverage before risky change.", "architecture"))
    if arch.get("is_monorepo"):
        risks.append(Risk("medium", "Monorepo — verify no unintended cross-workspace impact.", "architecture"))

    for rule in config.get("domain_rules", []):
        risks.append(Risk("high", f"Must not violate: {rule}", "domain_rule"))

    return risks


def score(risks: list[Risk]) -> int:
    return sum(_SEV_WEIGHT.get(r.severity, 1) for r in risks)


def level(risks: list[Risk]) -> str:
    if any(r.severity == "high" for r in risks):
        return "high"
    if any(r.severity == "medium" for r in risks):
        return "medium"
    return "low" if risks else "minimal"


class RiskEngine:
    """Named engine wrapper over the risk functions (reused by the Decision
    Engine). No new logic — single source of truth stays in this module."""

    name = "risk"

    def assess(self, request: str, arch: dict[str, Any] | None = None,
               config: dict[str, Any] | None = None) -> dict[str, Any]:
        risks = analyze(request, arch, config)
        return {
            "risks": risks,
            "level": level(risks),
            "score": score(risks),
            "messages": [f"[{r.severity}] {r.message}" for r in risks],
        }
