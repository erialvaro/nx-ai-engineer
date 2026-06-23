"""Policies — architectural/security rules surfaced to agents and gates.

Combines the framework's non-negotiable rules with the project's `domain_rules`
(tenant isolation, PII, etc.) from config. Pure data + helpers; no side effects.
"""
from __future__ import annotations

from typing import Any

CORE_POLICIES = [
    "Never break backward compatibility of public APIs/contracts.",
    "Never remove logs or weaken observability.",
    "Never change authentication/authorization without tests.",
    "Never cause data loss; migrations must be reversible.",
    "Always reuse existing services; never duplicate endpoints.",
    "Always add/update tests for behavior changes.",
    "Never touch another agent's forbidden paths.",
]


def all_policies(config: dict[str, Any] | None = None) -> list[str]:
    config = config or {}
    return [*CORE_POLICIES, *(f"[domain] {r}" for r in config.get("domain_rules", []))]


def violations(text: str, config: dict[str, Any] | None = None) -> list[str]:
    """Naive checker: flags policy keywords that appear as risky phrases. Intended
    as a lightweight advisory, not a substitute for review."""
    flags = []
    low = (text or "").lower()
    if "drop table" in low or "delete from" in low and "where" not in low:
        flags.append("possible destructive data operation")
    if "auth" in low and "test" not in low:
        flags.append("auth change without an obvious test reference")
    return flags
