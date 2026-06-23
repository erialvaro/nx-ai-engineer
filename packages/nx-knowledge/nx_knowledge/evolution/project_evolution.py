"""Project Evolution — enrich structured project knowledge after each execution.

After every agent execution the platform records what the change *touched*, by
classifying the **changed file paths and metadata** (never by reading code) into
the Project Brain facets:

    modules · services · APIs · entities (database) · tests · workflows ·
    integrations · dependencies · architectural patterns · fixed bugs ·
    technical decisions · lessons learned · related files (paths only)

Hard rules:
- **Never store code.** Only paths, names, counts and structured metadata.
- **Never store model responses.** Agent output text is never persisted here.
- The Brain's `looks_like_code` guard is a second line of defense.

Classification is path/metadata based (deterministic, offline) — it does not
interpret code or generate answers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from nx_core import agents as agents_mod
from ..memory.brain import ProjectBrain

_MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml",
    "pom.xml", "build.gradle", "composer.json", "Gemfile", "pubspec.yaml",
    "pnpm-lock.yaml", "package-lock.json", "poetry.lock",
}

# Path-token signatures (lower-cased path contains any token => bucket).
_SIGNATURES = {
    "services": ("/service", "services/", "usecase", "/domain/"),
    "apis": ("/api/", "/api", "routes", "controller", "endpoint", "handler", "graphql"),
    "entities": ("model", "entit", "migration", "schema", ".sql", ".prisma", "repositor"),
    "tests": ("test", "spec", "__tests__", "/e2e", "cypress"),
    "integrations": ("dockerfile", "docker-compose", ".github/workflows", "terraform",
                     "/k8s/", "helm", "webhook", "integration", "cloudbuild", "/ci/"),
}
_FIX_WORDS = ("fix", "bug", "hotfix", "patch", "regression", "correct")


class ProjectEvolutionEngine:
    name = "project-evolution"

    def __init__(self, brain: ProjectBrain | None = None) -> None:
        self.brain = brain or ProjectBrain()

    # -- main entry: called after each execution ------------------------- #
    def evolve(self, retro: dict[str, Any]) -> dict[str, Any]:
        files = [f for f in (retro.get("files_changed") or []) if isinstance(f, str)][:80]
        goal = (retro.get("request") or "")[:120]
        success = bool(retro.get("strategy_success"))
        b = self._classify(files)

        # Key/value facets — accumulate impact counts per item.
        for m in b["modules"]:
            self._bump("modules", m, goal)
        for s in b["services"]:
            self._bump("services", s, goal, owner="backend", path=s)
        for a in b["apis"]:
            self._bump("apis", a, goal, path=a)
        for e in b["entities"]:
            self._bump("database", e, goal, path=e)
        for t in b["tests"]:
            self._bump("tests", t, goal, path=t)
        for i in b["integrations"]:
            self._bump("integrations", i, goal, path=i)
        for d in b["dependencies"]:
            self._bump("dependencies", d, goal, path=d)

        # Architectural patterns from the discovered architecture.
        arch = self.brain.get("architecture", "current") or {}
        for fw in (arch.get("frameworks") or [])[:10]:
            self._bump("patterns", fw, goal, source="architecture")

        # Fixed bugs — when a fix-style goal succeeded.
        if success and any(w in goal.lower() for w in _FIX_WORDS):
            self.brain.append("bugs", {"fixed": goal, "files": b["related"][:10],
                                       "status": "fixed"})

        # Technical decisions (structured, from the decision — no model text).
        for d in (retro.get("decisions") or []):
            self.brain.append("decisions", {
                "goal": goal, "workflow": d.get("workflow"),
                "agents": d.get("agents"), "risk_level": d.get("risk_level")})

        # Lessons learned.
        if int(retro.get("failures", 0)) > 0 or int(retro.get("retries", 0)) > 0:
            self.brain.append("lessons", {
                "goal": goal, "note": "approach needed rework",
                "failures": retro.get("failures"), "retries": retro.get("retries"),
                "agents": retro.get("agents_used")})
        elif success:
            self.brain.append("lessons", {
                "goal": goal, "note": "strategy succeeded",
                "workflow": retro.get("workflow")})

        # Consolidated evolution record + related files (paths only).
        self.brain.append("knowledge", {
            "kind": "evolution", "goal": goal,
            "modules": sorted(b["modules"]), "services": b["services"][:10],
            "apis": b["apis"][:10], "entities": b["entities"][:10],
            "tests": b["tests"][:10], "integrations": b["integrations"][:10],
            "dependencies": b["dependencies"][:10], "related_files": b["related"][:20]})

        return {k: len(v) for k, v in b.items()}

    # -- classification (paths/metadata only) ---------------------------- #
    def _classify(self, files: list[str]) -> dict[str, list]:
        reg = agents_mod.registry({})
        out: dict[str, Any] = {k: [] for k in (
            "services", "apis", "entities", "tests", "integrations",
            "dependencies", "related")}
        modules: set[str] = set()
        for f in files:
            out["related"].append(f)
            top = f.split("/")[0] if "/" in f else "."
            if top != "." and not top.startswith("."):  # skip config/.dot dirs
                modules.add(top)
            low = f.lower()
            name = Path(f).name
            for facet, tokens in _SIGNATURES.items():
                if any(t in low for t in tokens):
                    out[facet].append(f)
            if name in _MANIFESTS:
                out["dependencies"].append(f)
        out["modules"] = sorted(modules)
        # de-dup
        for k in out:
            if isinstance(out[k], list):
                out[k] = sorted(dict.fromkeys(out[k]))
        return out

    def _bump(self, facet: str, key: str, goal: str, **extra: Any) -> None:
        rec = self.brain.get(facet, key) or {}
        rec["impacted"] = int(rec.get("impacted", 0)) + 1
        rec["last_goal"] = goal
        for k, v in extra.items():
            rec.setdefault(k, v)
        self.brain.put(facet, key, rec)

    # -- inspection ------------------------------------------------------- #
    def summary(self) -> dict[str, int]:
        kv = ["modules", "services", "apis", "database", "tests", "integrations",
              "dependencies", "patterns"]
        logs = ["bugs", "decisions", "lessons"]
        s = {f: len(self.brain.get(f) or {}) for f in kv}
        s.update({f: len(self.brain.read_log(f)) for f in logs})
        return s
