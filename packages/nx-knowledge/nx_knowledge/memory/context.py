"""Context Engine — builds the *minimal* context an agent needs.

No agent ever receives the whole project. The ContextBuilder runs a set of
resolvers (files, services, APIs, tests, docs, dependencies), ranks each result
by relevance, keeps the top-N per category, and reports the estimated context
reduction. Results are cached with version-based invalidation (see cache.py).

**Knowledge Providers:** the Context Engine never reads a knowledge source
directly. The project's file list comes from the `FilesystemProvider`, and docs/
patterns are enriched from the other providers (Markdown/ADR/Project-Brain) via
the Knowledge Registry. See `aies.knowledge`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable

from nx_core import agents as agents_mod
from nx_core.kernel.domain import AgentContext
from ..knowledge.registry import KnowledgeRegistry
from . import cache as cache_mod

_MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml",
    "pom.xml", "build.gradle", "composer.json", "Gemfile", "pubspec.yaml",
}
# How many items to keep per category.
_LIMITS = {"files": 12, "services": 8, "apis": 8, "tests": 8, "docs": 5, "deps": 6}


@dataclass
class Ranked:
    item: str
    score: float
    reason: str


@dataclass
class ContextResult:
    context: AgentContext
    total_files: int
    included_files: int
    estimated_reduction: float  # 0..1 fraction of the repo omitted
    cached: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "context": self.context.as_dict(),
            "total_files": self.total_files,
            "included_files": self.included_files,
            "estimated_reduction": self.estimated_reduction,
            "cached": self.cached,
        }


@runtime_checkable
class Resolver(Protocol):
    category: str

    def resolve(self, *, subtask, agent_spec, files: list[str], arch: dict) -> list[Ranked]:
        ...


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", (text or "").lower())}


def _base(area: str) -> str:
    return area.rstrip("/*")


class FilesResolver:
    category = "files"

    def resolve(self, *, subtask, agent_spec, files, arch):
        words = _words(subtask.objective)
        out: list[Ranked] = []
        for f in files:
            score, reasons = 0.0, []
            if agent_spec and agent_spec.owns(f):
                score += 5; reasons.append("owned")
            for a in subtask.areas:
                b = _base(a)
                if b and f.startswith(b):
                    score += 3; reasons.append("in area"); break
            low = f.lower()
            if any(w in low for w in words):
                score += 2; reasons.append("name match")
            if score > 0:
                out.append(Ranked(f, score, ",".join(reasons)))
        return out


class _TokenResolver:
    tokens: tuple[str, ...] = ()
    category = ""

    def resolve(self, *, subtask, agent_spec, files, arch):
        out = []
        for f in files:
            segs = f.lower()
            if any(t in segs for t in self.tokens):
                score = 2.0
                for a in subtask.areas:
                    if _base(a) and f.startswith(_base(a)):
                        score += 2; break
                out.append(Ranked(f, score, "matched: " + "/".join(self.tokens)))
        return out


class ServicesResolver(_TokenResolver):
    category = "services"
    tokens = ("service", "services", "usecase", "domain")


class ApisResolver(_TokenResolver):
    category = "apis"
    tokens = ("api/", "routes", "controller", "endpoint", "handler", "/api")


class TestsResolver(_TokenResolver):
    category = "tests"
    tokens = ("test", "spec", "__tests__", "e2e")


class DocsResolver:
    category = "docs"

    def resolve(self, *, subtask, agent_spec, files, arch):
        out = []
        for f in files:
            low = f.lower()
            if low.endswith(".md") or low.startswith("docs/") or "/docs/" in low:
                out.append(Ranked(f, 1.0, "documentation"))
        return out


class DependencyResolver:
    category = "deps"

    def resolve(self, *, subtask, agent_spec, files, arch):
        out = []
        for f in files:
            if Path(f).name in _MANIFESTS:
                out.append(Ranked(f, 1.0, "manifest"))
        return out


DEFAULT_RESOLVERS = [
    FilesResolver(), ServicesResolver(), ApisResolver(),
    TestsResolver(), DocsResolver(), DependencyResolver(),
]


class ContextBuilder:
    def __init__(self, *, resolvers: Optional[list] = None, bus=None,
                 limits: Optional[dict] = None,
                 knowledge: Optional[KnowledgeRegistry] = None) -> None:
        self._resolvers = resolvers or DEFAULT_RESOLVERS
        self._bus = bus
        self._limits = {**_LIMITS, **(limits or {})}
        self._knowledge = knowledge        # injected registry (else built lazily)

    def _registry(self, config: dict) -> KnowledgeRegistry:
        if self._knowledge is None:
            # The Context Engine retrieves through the Knowledge Engine (the flow
            # Brain → Knowledge Engine → Providers → Context). We inject a Brain
            # so the brain provider works (the knowledge layer never imports memory).
            from ..knowledge.engine import KnowledgeEngine
            from .brain import ProjectBrain
            self._knowledge = KnowledgeEngine(ProjectBrain(), config=config)
        # Accept either a KnowledgeEngine (use its registry) or a raw registry.
        return getattr(self._knowledge, "registry", self._knowledge)

    def build(self, *, agent: str, subtask, config: Optional[dict] = None,
              arch: Optional[dict] = None, use_cache: bool = True) -> ContextResult:
        config = config or {}
        arch = arch or {}
        knowledge = self._registry(config)
        fs = knowledge.get("filesystem")

        # ALL file knowledge comes through the Filesystem Provider (no os.walk here).
        files = fs.paths()
        version = fs.version()
        key = cache_mod.make_key(agent, subtask.id, subtask.objective, version)

        if use_cache:
            hit = cache_mod.read(key)
            if hit:
                res = self._from_cache(hit)
                self._emit(res, agent, subtask, cached=True)
                return res

        agent_spec = agents_mod.registry(config).get(agent)

        buckets: dict[str, list[Ranked]] = {}
        for r in self._resolvers:
            ranked = r.resolve(subtask=subtask, agent_spec=agent_spec, files=files, arch=arch)
            ranked.sort(key=lambda x: (-x.score, x.item))
            buckets[r.category] = ranked[: self._limits.get(r.category, 10)]

        file_docs = [r.item for r in buckets.get("docs", [])]
        ctx = AgentContext(
            agent=agent, subtask_id=subtask.id,
            files=[r.item for r in buckets.get("files", [])],
            services=[r.item for r in buckets.get("services", [])],
            apis=[r.item for r in buckets.get("apis", [])],
            tests=[r.item for r in buckets.get("tests", [])],
            docs=list(file_docs),
            patterns=list((arch.get("frameworks") or []))[:8],
            acceptance=list(getattr(subtask, "acceptance", []) or []),
        )

        # Reduction is measured against FILES only (file-derived inclusion), so
        # provider enrichment below never distorts the metric.
        included = len({*ctx.files, *ctx.services, *ctx.apis, *ctx.tests, *file_docs})
        total = max(1, len(files))
        reduction = round(1 - included / total, 4)

        # Knowledge-provider enrichment: docs (Markdown/ADR) + patterns (Brain).
        self._enrich(ctx, knowledge, subtask)
        # Knowledge-graph enrichment: related elements (APIs/tests/ADRs/bugs/…)
        # connected to the context files. ENRICHMENT ONLY — never replaces the
        # model's reasoning.
        self._graph_enrich(ctx)

        res = ContextResult(context=ctx, total_files=total, included_files=included,
                            estimated_reduction=reduction)
        if use_cache:
            cache_mod.write(key, res.as_dict())
        self._emit(res, agent, subtask, cached=False)
        return res

    def _enrich(self, ctx: AgentContext, knowledge: KnowledgeRegistry, subtask) -> None:
        """Pull structured knowledge from the non-filesystem providers (docs from
        Markdown/ADR, patterns from the Project Brain). Purely additive."""
        scope = {"query": getattr(subtask, "objective", ""),
                 "limit": self._limits.get("docs", 5)}
        try:
            doc_items = knowledge.retrieve(scope, providers=["markdown", "adr"])
            extra_docs = [it.ref for it in doc_items]
            seen = set(ctx.docs)
            for d in extra_docs:
                if d not in seen:
                    ctx.docs.append(d)
                    seen.add(d)
            ctx.docs = ctx.docs[: self._limits.get("docs", 5) + 4]
        except Exception:
            pass
        try:
            brain_items = knowledge.retrieve({"limit": 4}, providers=["project-brain"])
            pats = list(ctx.patterns)
            for it in brain_items:
                tag = f"{it.kind}:{it.ref}"
                if tag not in pats:
                    pats.append(tag)
            ctx.patterns = pats[:10]
        except Exception:
            pass

    def _graph_enrich(self, ctx: AgentContext) -> None:
        """Add elements related (via the Knowledge Graph) to the context files.
        Enrichment only — additive, capped; never replaces the model's reasoning."""
        engine = self._knowledge
        if not hasattr(engine, "enrich_context"):
            return
        try:
            related = engine.enrich_context(list(ctx.files))
        except Exception:
            return
        if not related:
            return

        def merge(target: list[str], items: list[str], cap: int) -> list[str]:
            seen = set(target)
            for x in items:
                if x not in seen:
                    target.append(x)
                    seen.add(x)
            return target[:cap]

        ctx.apis = merge(ctx.apis, related.get("api", []), self._limits.get("apis", 8) + 4)
        ctx.tests = merge(ctx.tests, related.get("test", []), self._limits.get("tests", 8) + 4)
        ctx.services = merge(ctx.services, related.get("service", []),
                             self._limits.get("services", 8) + 4)
        ctx.docs = merge(ctx.docs, related.get("doc", []), self._limits.get("docs", 5) + 6)
        tags = [f"adr:{x}" for x in related.get("adr", [])] + \
               [f"bug:{x}" for x in related.get("bug", [])]
        ctx.patterns = merge(ctx.patterns, tags, 14)

    def _from_cache(self, hit: dict) -> ContextResult:
        c = hit["context"]
        ctx = AgentContext(
            agent=c["agent"], subtask_id=c["subtask_id"], files=c.get("files", []),
            services=c.get("services", []), apis=c.get("apis", []),
            tests=c.get("tests", []), docs=c.get("docs", []),
            patterns=c.get("patterns", []), acceptance=c.get("acceptance", []),
        )
        return ContextResult(context=ctx, total_files=hit["total_files"],
                             included_files=hit["included_files"],
                             estimated_reduction=hit["estimated_reduction"], cached=True)

    def _emit(self, res: ContextResult, agent: str, subtask, cached: bool) -> None:
        if self._bus:
            self._bus.emit("context.built", {
                "agent": agent, "subtask": subtask.id,
                "included": res.included_files, "total": res.total_files,
                "estimated_reduction": res.estimated_reduction, "cached": cached,
            })
