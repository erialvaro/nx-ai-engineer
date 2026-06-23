"""Recommendation Engine — recommends how to approach a new request based on
what worked before (similar past tasks + aggregated experience + patterns)."""
from __future__ import annotations

from collections import Counter
from typing import Any, Optional

from ..memory.brain import ProjectBrain
from .experience_analyzer import ExperienceAnalyzer
from .similarity import SimilarTaskDetector


class RecommendationEngine:
    name = "recommendation"

    def __init__(self, brain: Optional[ProjectBrain] = None, *,
                 similarity: Optional[SimilarTaskDetector] = None,
                 analyzer: Optional[ExperienceAnalyzer] = None) -> None:
        self.brain = brain or ProjectBrain()
        self.similarity = similarity or SimilarTaskDetector()
        self.analyzer = analyzer or ExperienceAnalyzer()

    def recommend(self, request: str) -> dict[str, Any]:
        similar = self.similarity.find_similar(request, k=5, brain=self.brain)
        insights = self.analyzer.analyze(self.brain)

        # Recommend agents = most frequent agents across similar past tasks.
        agent_freq: Counter = Counter()
        wf_freq: Counter = Counter()
        failed_similar = 0
        for hit in similar:
            for a in hit.meta.get("agents", []):
                agent_freq[a] += 1
            if hit.meta.get("workflow"):
                wf_freq[hit.meta["workflow"]] += 1
            if hit.meta.get("strategy_success") is False:
                failed_similar += 1

        warnings: list[str] = []
        if insights.get("rework_rate", 0) and insights["rework_rate"] >= 0.3:
            warnings.append(f"Historically high rework rate ({insights['rework_rate']}).")
        if failed_similar:
            warnings.append(f"{failed_similar} similar past task(s) did not succeed — review the approach.")
        if not similar:
            warnings.append("No similar past task found — recommendation is heuristic.")

        return {
            "similar_tasks": [{"request_id": h.doc_id, "score": h.score,
                               "workflow": h.meta.get("workflow"),
                               "status": h.meta.get("status")} for h in similar],
            "recommended_agents": [a for a, _ in agent_freq.most_common(8)],
            "recommended_workflow": (wf_freq.most_common(1)[0][0] if wf_freq else None),
            "warnings": warnings,
            "based_on_runs": insights.get("runs", 0),
        }
