"""Knowledge Graph — automatic relationships between project elements.

The Knowledge Engine builds a typed graph that connects the project's knowledge:

    Service → API → Database → Migration → Test → ADR → Bug → Feature
            → Sprint → Documentation → Obsidian

Edges are **inferred automatically** from structured knowledge (never by reading
code):
  - **co-occurrence**: elements touched together in one execution (Project
    Evolution records) form the Service→API→DB→Test chain;
  - **path proximity**: elements in the same module are related;
  - **ADR references / doc links** (from the providers);
  - **fixed bugs → the feature that fixed them**;
  - **sprints** group features by date; **docs → Obsidian**.

The graph is used **only to enrich the context** delivered to agents — it never
makes decisions, interprets code, generates answers, or replaces the model's
reasoning. It surfaces *related elements*, nothing more.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util

# The canonical element order (drives Mermaid layout / chain direction).
TYPE_ORDER = ["feature", "sprint", "service", "api", "entity", "migration",
              "test", "integration", "dependency", "module", "adr", "bug",
              "doc", "obsidian"]


@dataclass
class GraphNode:
    id: str
    type: str
    label: str
    meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "label": self.label, "meta": self.meta}


@dataclass
class GraphEdge:
    source: str
    target: str
    kind: str

    def as_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target, "kind": self.kind}


class KnowledgeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._adj: dict[str, set[str]] = {}
        self._seen_edges: set[tuple] = set()

    # -- construction ---------------------------------------------------- #
    def add_node(self, node_id: str, type: str, label: str,
                 meta: Optional[dict] = None) -> str:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id, type, label, meta or {})
            self._adj[node_id] = set()
        elif meta:
            self.nodes[node_id].meta.update(meta)
        return node_id

    def add_edge(self, source: str, target: str, kind: str) -> None:
        if source == target or source not in self.nodes or target not in self.nodes:
            return
        key = (source, target, kind)
        if key in self._seen_edges:
            return
        self._seen_edges.add(key)
        self.edges.append(GraphEdge(source, target, kind))
        self._adj[source].add(target)
        self._adj[target].add(source)  # undirected adjacency for neighborhood

    # -- queries --------------------------------------------------------- #
    def nodes_of_type(self, type: str) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.type == type]

    def neighbors(self, node_id: str, depth: int = 1) -> set[str]:
        seen: set[str] = set()
        frontier = {node_id}
        for _ in range(max(1, depth)):
            nxt: set[str] = set()
            for n in frontier:
                for m in self._adj.get(n, ()):
                    if m not in seen and m != node_id:
                        seen.add(m)
                        nxt.add(m)
            frontier = nxt
        return seen

    def find_by_path(self, path: str) -> list[str]:
        return [nid for nid, n in self.nodes.items() if n.meta.get("path") == path]

    def related_elements(self, paths: list[str], *, depth: int = 2,
                         types: Optional[set[str]] = None) -> dict[str, list[str]]:
        """Elements related to a set of file paths, grouped by type — the
        enrichment the Context Engine adds to an agent's context."""
        seeds: set[str] = set()
        for p in paths:
            seeds.update(self.find_by_path(p))
        out: dict[str, list[str]] = {}
        related: set[str] = set()
        for s in seeds:
            related.update(self.neighbors(s, depth))
        related -= seeds
        for nid in related:
            node = self.nodes.get(nid)
            if not node:
                continue
            if types and node.type not in types:
                continue
            out.setdefault(node.type, []).append(node.meta.get("path") or node.label)
        return {k: sorted(dict.fromkeys(v)) for k, v in out.items()}

    # -- export ---------------------------------------------------------- #
    def stats(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for n in self.nodes.values():
            by_type[n.type] = by_type.get(n.type, 0) + 1
        return {"nodes": len(self.nodes), "edges": len(self.edges), "by_type": by_type}

    def as_dict(self) -> dict[str, Any]:
        return {"nodes": [n.as_dict() for n in self.nodes.values()],
                "edges": [e.as_dict() for e in self.edges], "stats": self.stats()}

    def to_mermaid(self, limit: int = 80) -> str:
        def nid(x: str) -> str:
            return "N" + util.short_hash(x, 8)
        lines = ["```mermaid", "graph LR"]
        shown = list(self.edges)[:limit]
        used = set()
        for e in shown:
            used.add(e.source)
            used.add(e.target)
        for u in used:
            n = self.nodes[u]
            lines.append(f'  {nid(u)}["{n.type}: {n.label[:24]}"]')
        for e in shown:
            lines.append(f"  {nid(e.source)} -->|{e.kind}| {nid(e.target)}")
        lines.append("```")
        return "\n".join(lines)


class KnowledgeGraphBuilder:
    """Builds a KnowledgeGraph from the Project Brain (structured knowledge) and,
    optionally, the provider registry (ADR/markdown relationships)."""

    def __init__(self, brain: Any, *, registry: Any = None) -> None:
        self.brain = brain
        self.registry = registry

    def build(self) -> KnowledgeGraph:
        g = KnowledgeGraph()
        self._from_evolution_records(g)
        self._from_bugs(g)
        self._from_sprints(g)
        self._from_providers(g)
        return g

    # -- co-occurrence (the chain) from Project Evolution records -------- #
    _LISTS = [("service", "services"), ("api", "apis"), ("entity", "entities"),
              ("test", "tests"), ("integration", "integrations"),
              ("dependency", "dependencies")]

    def _node_for(self, g: KnowledgeGraph, type: str, path: str) -> str:
        t = "migration" if (type == "entity" and "migration" in path.lower()) else type
        return g.add_node(f"{t}:{path}", t, Path(path).name, {"path": path})

    def _from_evolution_records(self, g: KnowledgeGraph) -> None:
        for rec in self._log("knowledge"):
            if rec.get("kind") != "evolution":
                continue
            goal = rec.get("goal", "")
            fid = g.add_node(f"feature:{util.slugify(goal, 40)}", "feature", goal[:48],
                             {"goal": goal})
            typed: dict[str, list[str]] = {}
            for type, key in self._LISTS:
                paths = (rec.get(key) or [])[:10]
                typed[type] = [self._node_for(g, type, p) for p in paths]
                for n in typed[type]:
                    g.add_edge(fid, n, "delivers")
            for m in (rec.get("modules") or [])[:10]:
                mid = g.add_node(f"module:{m}", "module", m, {})
                g.add_edge(fid, mid, "in-module")
            # the canonical chain (co-occurrence within one execution).
            # Note: migration paths were typed as "migration:" nodes by _node_for,
            # so typed["entity"] holds both entity: and migration: node ids.
            entities = typed.get("entity", [])
            ents = [n for n in entities if n.startswith("entity:")]
            migs = [n for n in entities if n.startswith("migration:")]
            for s in typed.get("service", []):
                for a in typed.get("api", []):
                    g.add_edge(s, a, "serves")
            for a in typed.get("api", []):
                for e in entities:
                    g.add_edge(a, e, "uses")
            for e in ents:
                for m in migs:
                    g.add_edge(e, m, "migrates")
            for t in typed.get("test", []):
                for x in typed.get("service", []) + typed.get("api", []):
                    g.add_edge(t, x, "covers")

    # -- bugs -> feature + elements -------------------------------------- #
    def _from_bugs(self, g: KnowledgeGraph) -> None:
        for i, bug in enumerate(self._log("bugs")):
            label = str(bug.get("fixed") or bug.get("goal") or f"bug-{i}")[:48]
            bid = g.add_node(f"bug:{i}", "bug", label, {"status": bug.get("status")})
            goal = bug.get("fixed") or ""
            if goal:
                fid = f"feature:{util.slugify(goal, 40)}"
                if fid in g.nodes:
                    g.add_edge(bid, fid, "fixed-in")
            for f in (bug.get("files") or [])[:10]:
                for nid in g.find_by_path(f):
                    g.add_edge(bid, nid, "affects")

    # -- sprints group features by date ---------------------------------- #
    def _from_sprints(self, g: KnowledgeGraph) -> None:
        for r in self._log("retrospectives"):
            goal = r.get("request", "")
            if not goal:
                continue
            fid = f"feature:{util.slugify(goal, 40)}"
            if fid not in g.nodes:
                fid = g.add_node(fid, "feature", goal[:48], {"goal": goal})
            date = (r.get("ts") or "")[:10] or "undated"
            sid = g.add_node(f"sprint:{date}", "sprint", f"sprint {date}", {"date": date})
            g.add_edge(sid, fid, "in-sprint")

    # -- providers: ADR refs, doc links, obsidian ------------------------ #
    def _from_providers(self, g: KnowledgeGraph) -> None:
        if self.registry is None:
            return
        obsidian = g.add_node("obsidian:vault", "obsidian", "Obsidian vault", {})
        try:
            adr = self.registry.get("adr")
            for it in (adr.catalog() if adr else []):
                num = it.metadata.get("number", 0)
                g.add_node(f"adr:{num:04d}", "adr", it.title[:48], {"status": it.metadata.get("status")})
            for it in (adr.catalog() if adr else []):
                a = f"adr:{it.metadata.get('number', 0):04d}"
                for r in it.relationships:
                    if r.kind == "references":
                        g.add_edge(a, f"adr:{int(r.target.split(':')[-1]):04d}", "references")
        except Exception:
            pass
        try:
            md = self.registry.get("markdown")
            for it in (md.catalog() if md else []):
                did = g.add_node(f"doc:{it.ref}", "doc", it.title[:48], {"path": it.ref})
                g.add_edge(did, obsidian, "reflected-in")
            for it in (md.catalog() if md else []):
                for r in it.relationships:
                    if r.kind == "links-to":
                        tgt = f"doc:{r.target.split(':', 1)[-1]}"
                        if tgt in g.nodes:
                            g.add_edge(f"doc:{it.ref}", tgt, "links-to")
        except Exception:
            pass

    # -- defensive ------------------------------------------------------- #
    def _log(self, facet: str) -> list[dict]:
        try:
            return self.brain.read_log(facet)
        except Exception:
            return []
