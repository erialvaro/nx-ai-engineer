"""Pattern Discovery — mines recurring patterns from retrospectives and writes
them back into the Brain's `patterns` facet (knowledge only, never code)."""
from __future__ import annotations

from collections import Counter
from typing import Any

from ..memory.brain import ProjectBrain


class PatternDiscovery:
    name = "pattern-discovery"

    def discover(self, retros: list[dict]) -> dict[str, Any]:
        agent_sets: Counter = Counter()
        failure_prone: Counter = Counter()
        file_areas: Counter = Counter()
        for r in retros:
            agents = r.get("agents_used") or []
            if agents:
                agent_sets[tuple(sorted(agents))] += 1
            if int(r.get("failures", 0)) > 0:
                for a in agents:
                    failure_prone[a] += 1
            for f in r.get("files_changed", []) or []:
                top = f.replace("\\", "/").split("/")[0]   # normalize Windows paths
                file_areas[top] += 1
        return {
            "agent_sets": [{"agents": list(k), "count": v} for k, v in agent_sets.most_common(5)],
            "failure_prone": [{"agent": a, "count": c} for a, c in failure_prone.most_common(5)],
            "hot_areas": [{"area": a, "count": c} for a, c in file_areas.most_common(8)],
        }

    def persist(self, brain: ProjectBrain | None = None) -> dict[str, Any]:
        brain = brain or ProjectBrain()
        retros = [r for r in brain.read_log("retrospectives") if r.get("agents_used")]
        found = self.discover(retros)
        if found["agent_sets"]:
            brain.put("patterns", "recurring-agent-sets", {"sets": found["agent_sets"]})
        if found["failure_prone"]:
            brain.put("patterns", "failure-prone-agents", {"agents": found["failure_prone"]})
        if found["hot_areas"]:
            brain.put("patterns", "hot-areas", {"areas": found["hot_areas"]})
        return found
