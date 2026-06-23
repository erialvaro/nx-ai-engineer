"""Knowledge Engine — the single coordination point for the project's knowledge.

It unifies the three project memories and keeps them synchronized:

  - **Project Brain**  → operational memory (the canonical *current* state)
  - **Obsidian**       → organizational memory (a navigable view of the Brain)
  - **Git**            → historical memory (the immutable record)

Canonical flow:

    Project Brain → Knowledge Engine → Knowledge Providers → Obsidian
                  → Context Engine → Agents

The Knowledge Engine is the access point the Context Engine uses to retrieve
knowledge (Context never touches providers or the Brain directly). The Brain is
**injected** (duck-typed) so this layer never imports the Memory layer — keeping
the dependency graph acyclic.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util
from nx_providers.knowledge.base import KnowledgeItem, Relationship
from nx_providers.knowledge.graph import KnowledgeGraph, KnowledgeGraphBuilder
from nx_obsidian.knowledge.obsidian_sync import MANIFEST, ObsidianSync
from .contract import ContractBuilder, EngineeringContract
from .registry import KnowledgeRegistry, default_registry


class KnowledgeEngine:
    """The Project Knowledge Engine.

    Doctrine — it has EXACTLY five responsibilities and nothing more:
      1. **Discover** existing knowledge   (`discover`)
      2. **Index** knowledge               (`index`)
      3. **Relate** knowledge              (`relate`)
      4. **Update** knowledge              (`update`)
      5. **Deliver enriched context** to agents (`deliver_context`)

    It does NOT learn programming, improve AI models, or create reasoning
    mechanisms. **All intelligence belongs to the AI model.** This engine only
    **reduces the model's cognitive load**: the larger a project's history, the
    richer the context, the more assertive the implementation, and the fewer
    tokens consumed.
    """

    name = "knowledge-engine"

    # The five (and only five) responsibilities — see methods below.
    RESPONSIBILITIES = ("discover", "index", "relate", "update", "deliver_context")

    def __init__(self, brain: Any, *, config: Optional[dict] = None,
                 root: Optional[Path] = None, bus=None) -> None:
        self.brain = brain
        self.config = config or {}
        self.root = root or util.project_root()
        self.registry: KnowledgeRegistry = default_registry(
            root=self.root, config=self.config, brain=brain)
        self.obsidian = ObsidianSync(brain, config=self.config, root=self.root)
        self._graph: Optional[KnowledgeGraph] = None
        self._bus = None
        if bus is not None:
            self.attach(bus)

    # -- access point for the Context Engine ----------------------------- #
    def retrieve(self, scope: Optional[dict] = None,
                 providers: Optional[list[str]] = None) -> list[KnowledgeItem]:
        return self.registry.retrieve(scope, providers)

    def build_contract(self, task: str, agent: str, *, files: Optional[list] = None,
                       areas: Optional[list] = None) -> EngineeringContract:
        """Assemble the Engineering Contract for an agent+task — the declarative
        brief (context/knowledge/engineering packs/constraints/requirements) that
        precedes context delivery. Part of `deliver_context`; pure organization."""
        return ContractBuilder(self.brain, config=self.config, registry=self.registry).build(
            task, agent, files=files, areas=areas)

    def relationships(self) -> list[Relationship]:
        return self.registry.relationships()

    def get(self, provider: str):
        return self.registry.get(provider)

    # -- knowledge graph (automatic relationships between elements) ------- #
    def graph(self, *, rebuild: bool = False) -> KnowledgeGraph:
        if self._graph is None or rebuild:
            self._graph = KnowledgeGraphBuilder(self.brain, registry=self.registry).build()
        return self._graph

    def enrich_context(self, paths: list[str], *, depth: int = 2) -> dict[str, list[str]]:
        """Elements related (via the graph) to the agent's context files. Used
        ONLY to enrich the context handed to agents — it never decides or reasons.
        Returns {type: [paths/labels]} for apis/tests/services/docs/adr/bug/…"""
        try:
            return self.graph().related_elements(paths, depth=depth)
        except Exception:
            return {}

    # ================================================================== #
    # The FIVE responsibilities — the engine's entire public contract.
    # (No reasoning, no learning-to-code, no model improvement.)
    # ================================================================== #
    def discover(self) -> dict[str, int]:
        """(1) Discover existing knowledge from every source (providers scan)."""
        return self.registry.index_all()

    def index(self) -> int:
        """(2) Index discovered knowledge into a single retrievable catalog.
        Returns the number of indexed knowledge items."""
        return len(self.registry.catalog())

    def relate(self, *, rebuild: bool = False) -> KnowledgeGraph:
        """(3) Relate knowledge — the automatic relationship graph between
        elements (Service→API→DB→Migration→Test→ADR→Bug→Feature→…)."""
        return self.graph(rebuild=rebuild)

    def update(self, *, commit: bool = False) -> dict[str, Any]:
        """(4) Update knowledge — keep the three memories (Brain/Obsidian/Git)
        synchronized and the graph current."""
        return self.sync(commit=commit)

    def deliver_context(self, paths: list[str], *, depth: int = 2) -> dict[str, list[str]]:
        """(5) Deliver enriched context to agents — related elements only.
        It NEVER reasons, decides, or replaces the model; it just lowers the
        model's cognitive load (richer history → richer context → fewer tokens)."""
        return self.enrich_context(paths, depth=depth)

    # -- automatic synchronization --------------------------------------- #
    def attach(self, bus) -> None:
        self._bus = bus
        bus.subscribe("pipeline.completed", lambda e: self._auto())
        bus.subscribe("adr.created", lambda e: self._auto())

    def _auto(self) -> None:
        try:
            self.sync()
        except Exception:
            pass  # best-effort; coordination must never break a run

    def sync(self, *, commit: bool = False) -> dict[str, Any]:
        """Bring the three memories into sync.
        1. Refresh providers (Git reflects history; Brain provider reflects state).
        2. Obsidian (organizational) ← Project Brain (operational).
        3. Optionally snapshot to Git (historical) — opt-in only.
        """
        try:
            self.registry.index_all()
        except Exception as exc:
            if self._bus is not None:
                self._bus.emit("knowledge.index_error", {"error": repr(exc)})
        obs: dict[str, Any] = {}
        try:
            obs = self.obsidian.sync()
        except Exception as exc:
            if self._bus is not None:
                self._bus.emit("knowledge.obsidian_error", {"error": repr(exc)})
        self._graph = None  # brain changed → graph rebuilds on next access
        committed = False
        if commit or self.config.get("knowledge_git_snapshot", False):
            committed = self._commit_snapshot()

        report = {
            "operational": {"memory": "Project Brain", "version": self._brain_version()},
            "organizational": {"memory": "Obsidian", "notes": obs.get("total"),
                               "written": obs.get("written"), "vault": obs.get("vault")},
            "historical": {"memory": "Git", "head": self._git_head(), "committed": committed},
        }
        if self._bus is not None:
            self._bus.emit("knowledge.synced", {
                "brain_version": report["operational"]["version"],
                "obsidian_notes": obs.get("total"), "committed": committed})
        return report

    def status(self) -> dict[str, Any]:
        """Synchronization state of the three memories."""
        manifest = util.read_json(Path(self.obsidian.vault) / MANIFEST, {}) or {}
        bv = self._brain_version()
        obs_bv = manifest.get("brain_version")
        in_sync = obs_bv == bv and manifest.get("count", 0) > 0
        return {
            "operational": {"memory": "Project Brain", "version": bv},
            "organizational": {"memory": "Obsidian", "vault": str(self.obsidian.vault),
                               "notes": manifest.get("count", 0), "brain_version": obs_bv,
                               "in_sync": in_sync},
            "historical": {"memory": "Git", "is_repo": util.is_git_repo(self.root),
                           "head": self._git_head(), "commits": self._commit_count()},
            "synchronized": in_sync,
            # Context richness grows with project history (more knowledge + edges
            # => richer context for agents => fewer tokens needed).
            "richness": self.graph().stats(),
        }

    # -- git (historical memory) ----------------------------------------- #
    def _commit_snapshot(self) -> bool:
        if not util.is_git_repo(self.root):
            return False
        cfg = util.config_root()
        util.git(["add", str(cfg / "brain"), str(cfg / "obsidian")], self.root)
        code, _, _ = util.git(
            ["commit", "-m", "chore(aies): knowledge snapshot"], self.root)
        return code == 0

    def _git_head(self) -> Optional[str]:
        if not util.is_git_repo(self.root):
            return None
        code, out, _ = util.git(["rev-parse", "--short", "HEAD"], self.root)
        return out if code == 0 and out else None

    def _commit_count(self) -> int:
        if not util.is_git_repo(self.root):
            return 0
        code, out, _ = util.git(["rev-list", "--count", "HEAD"], self.root)
        try:
            return int(out) if code == 0 else 0
        except ValueError:
            return 0

    def _brain_version(self) -> int:
        try:
            return int(self.brain.version())
        except Exception:
            return 0
