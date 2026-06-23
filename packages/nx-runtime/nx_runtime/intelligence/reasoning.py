"""Reasoning Engine — derives recommendations and a human-readable rationale
from the raw signals (selection, risk, parallelism, estimate).

It decides: need for Review, need for QA, whether work is parallelizable; and it
explains *why* (the chain of reasoning), so every decision is auditable.
"""
from __future__ import annotations

from typing import Any

_CODE_AGENTS = {"backend", "frontend", "database", "ai", "security", "devops"}


class ReasoningEngine:
    name = "reasoning"

    def reason(self, *, request: str, agents: list[str], risk_level: str,
               risk_messages: list[str], parallelism: int,
               estimate: dict) -> dict[str, Any]:
        code = [a for a in agents if a in _CODE_AGENTS]
        rationale: list[str] = []

        # Review: always for code/risky work; escalated when risk is medium+.
        needs_review = bool(code) or risk_level in ("medium", "high")
        if risk_level in ("medium", "high"):
            rationale.append(f"Review required — risk level is {risk_level}.")
        elif code:
            rationale.append("Review recommended — change touches product code.")
        else:
            rationale.append("Light review — no code change detected.")

        # QA: whenever code changes or risk is non-trivial.
        needs_qa = bool(code) or risk_level in ("medium", "high")
        rationale.append(
            "QA required — behavior changes need tests."
            if needs_qa else "QA optional — documentation/meta change only."
        )

        # Parallelism: more than one independent lane available.
        parallelizable = parallelism >= 2
        rationale.append(
            f"Parallelizable — up to {parallelism} agents can run concurrently."
            if parallelizable else "Sequential — dependencies serialize the work."
        )

        if risk_messages:
            rationale.append("Risks: " + "; ".join(risk_messages[:4]))
        rationale.append(
            f"Estimated effort {estimate.get('effort_points')} pts "
            f"(~{estimate.get('estimated_time_min_parallel')} min parallel, "
            f"~{estimate.get('estimated_cost_tokens')} tokens)."
        )

        return {
            "needs_review": needs_review,
            "needs_qa": needs_qa,
            "parallelizable": parallelizable,
            "rationale": rationale,
            "confidence": estimate.get("confidence", 0.5),
        }
