"""Engineering Contract — the declarative brief an agent receives for a task.

A contract is NOT a prompt. It is a structured, predictable declaration of what
applies to a task for a given agent:

    task → EngineeringContract → Context Builder → model → result → knowledge update

It assembles (it never reasons or decides):
  - context     : which files/areas are in scope
  - knowledge   : which ADRs/patterns to consider
  - engineering : which Engineering Packs apply (auto-attached by `applies_to`)
  - constraints : non-negotiable rules (project + packs)
  - requirements: mandatory tests / validations / checklists / ADRs (enforced at delivery)
  - brain       : which Project-Brain facets enter the context

Pack auto-application is purely declarative: a pack attaches to an agent when its
`applies_to` contains that agent or "*", with per-agent overrides from config.
This module only organizes data — all intelligence belongs to the model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class EngineeringContract:
    task: str
    agent: str
    context: dict[str, list[str]] = field(default_factory=lambda: {"files": [], "areas": []})
    knowledge: list[str] = field(default_factory=list)
    engineering: list[dict[str, Any]] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    requirements: dict[str, list[str]] = field(default_factory=lambda: {
        "tests": [], "validations": [], "checklists": [], "adrs": []})
    brain: list[str] = field(default_factory=list)
    # A matched design-reference profile (palette/type/mood) for design tasks, or
    # None. Injected only for the designer/frontend agents when the
    # `design-references` pack is installed and a reference fits the task.
    design_reference: Optional[dict[str, Any]] = None

    def packs(self) -> list[str]:
        return [e["pack"] for e in self.engineering]

    def as_dict(self) -> dict[str, Any]:
        return {
            "task": self.task, "agent": self.agent, "context": self.context,
            "knowledge": self.knowledge,
            "engineering": [{"pack": e["pack"], "title": e["title"]} for e in self.engineering],
            "constraints": self.constraints, "requirements": self.requirements,
            "brain": self.brain,
            "design_reference": self.design_reference,
        }

    def to_text(self) -> str:
        L = [f"task:\n  {self.task}", f"\nagent:\n  {self.agent}", "\ncontext:"]
        L.append("  files:" + ("" if self.context.get("files") else " []"))
        L += [f"    - {f}" for f in self.context.get("files", [])]
        if self.context.get("areas"):
            L.append("  areas:")
            L += [f"    - {a}" for a in self.context["areas"]]
        L.append("\nknowledge:" + ("" if self.knowledge else " []"))
        L += [f"  - {k}" for k in self.knowledge]
        L.append("\nengineering:" + ("" if self.engineering else " []"))
        L += [f"  - {e['title']}  ({e['pack']})" for e in self.engineering]
        L.append("\nconstraints:" + ("" if self.constraints else " []"))
        L += [f"  - {c}" for c in self.constraints]
        L.append("\nrequirements:")
        for key in ("tests", "validations", "checklists", "adrs"):
            vals = self.requirements.get(key) or []
            L.append(f"  {key}:" + ("" if vals else " []"))
            L += [f"    - {v}" for v in vals]
        L.append("\nbrain:" + ("" if self.brain else " []"))
        L += [f"  - {b}" for b in self.brain]
        dr = self.design_reference
        if dr:
            pal = (dr.get("palette") or {}).get("light", {}) or {}
            typo = dr.get("typography") or {}
            disp = (typo.get("display") or {}).get("family", "?")
            body = (typo.get("body") or {}).get("family", "?")
            L.append("\ndesign_reference:")
            L.append(f"  id:       {dr.get('id', '?')}")
            L.append(f"  name:     {dr.get('name', '?')}")
            L.append(f"  vertical: {dr.get('vertical', '?')}")
            L.append(f"  mood:     {', '.join(dr.get('mood', []))}")
            L.append("  palette (light): " + ", ".join(f"{k}:{v}" for k, v in pal.items()))
            L.append(f"  type:     {disp} (display) + {body} (body)")
            if dr.get("source"):
                L.append(f"  source:   {dr['source']}")
        return "\n".join(L) + "\n"


class ContractBuilder:
    """Assemble an EngineeringContract from the registry (incl. the Pack Provider),
    the Project Brain (duck-typed) and the project config. Pure organization."""

    def __init__(self, brain: Any = None, *, config: Optional[dict] = None, registry=None) -> None:
        self.brain = brain
        self.config = config or {}
        self.registry = registry

    # -- pack selection (declarative auto-application) ------------------- #
    def _installed_packs(self) -> list[dict[str, Any]]:
        prov = self.registry.get("packs") if self.registry else None
        if prov is None:
            return []
        out = []
        for it in prov.catalog():
            m = dict(it.metadata)
            m.setdefault("name", it.title)
            out.append(m)
        return out

    def _applicable(self, agent: str) -> list[dict[str, Any]]:
        override = ((self.config.get("contracts") or {}).get("agents") or {}).get(agent) or {}
        extra = set(override.get("packs") or [])
        exclude = set(override.get("exclude") or [])
        chosen = []
        for p in self._installed_packs():
            name = p.get("name")
            applies = p.get("applies_to") or []
            auto = ("*" in applies) or (agent in applies)
            if (auto or name in extra) and name not in exclude:
                chosen.append(p)
        chosen.sort(key=lambda p: p.get("name", ""))
        return chosen

    def requirements_for(self, agents) -> dict[str, Any]:
        """Aggregate the contract requirements of every pack that applies to any of
        `agents` — used to enforce the contract at delivery (no ADR retrieval)."""
        seen: set = set()
        packs: list[dict[str, Any]] = []
        for ag in agents:
            for p in self._applicable(ag):
                if p["name"] not in seen:
                    seen.add(p["name"])
                    packs.append(p)
        agg = {"packs": [p["name"] for p in packs], "tests": [], "validations": [], "checklists": []}
        for p in packs:
            agg["tests"] += p.get("mandatory_tests", [])
            agg["validations"] += p.get("validations", [])
            agg["checklists"] += p.get("checklists", [])
        for k in ("tests", "validations", "checklists"):
            agg[k] = list(dict.fromkeys(agg[k]))
        agg["mandates_tests"] = bool(agg["tests"])
        return agg

    # -- build ----------------------------------------------------------- #
    def build(self, task: str, agent: str, *, files: Optional[list[str]] = None,
              areas: Optional[list[str]] = None) -> EngineeringContract:
        packs = self._applicable(agent)
        engineering, constraints, brain_facets = [], [], []
        req = {"tests": [], "validations": [], "checklists": [], "adrs": []}
        for p in packs:
            engineering.append({"pack": p["name"], "title": p.get("title", p["name"]),
                                "domain": p.get("domain", ""),
                                "policies": p.get("policies", [])[:6],
                                "checklists": p.get("checklists", [])})
            # the headline non-negotiable of each pack becomes a constraint
            pol = p.get("policies") or []
            if pol:
                constraints.append(f"[{p['name']}] {pol[0]}")
            req["tests"] += p.get("mandatory_tests", [])
            req["validations"] += p.get("validations", [])
            req["checklists"] += p.get("checklists", [])
            req["adrs"] += p.get("required_adrs", [])
            brain_facets += p.get("brain_facets", [])

        # project-level constraints
        for r in (self.config.get("domain_rules") or []):
            constraints.append(str(r))
        override = ((self.config.get("contracts") or {}).get("agents") or {}).get(agent) or {}
        constraints += [str(c) for c in (override.get("constraints") or [])]

        # knowledge: relevant ADRs from the registry + pack-required ADRs
        knowledge = list(dict.fromkeys(req["adrs"]))
        if self.registry is not None:
            try:
                scope = {"query": task, "areas": areas or [], "limit": 8}
                for it in self.registry.retrieve(scope, providers=["adr", "markdown"]):
                    label = it.title or it.ref
                    if label and label not in knowledge:
                        knowledge.append(label)
            except Exception:
                pass

        # de-dup requirement lists while preserving order
        for k in req:
            req[k] = list(dict.fromkeys(req[k]))

        # design reference: only for design agents, only when the pack is installed
        # and applies to this agent (i.e. it is among `packs`).
        design_reference = None
        if agent in ("designer", "frontend", "mobile") and any(
                p.get("name") == "design-references" for p in packs):
            design_reference = self._select_reference(task)

        return EngineeringContract(
            task=task, agent=agent,
            context={"files": list(files or []), "areas": list(areas or [])},
            knowledge=knowledge[:12],
            engineering=engineering,
            constraints=list(dict.fromkeys(constraints)),
            requirements=req,
            brain=list(dict.fromkeys(brain_facets)),
            design_reference=design_reference,
        )

    def _select_reference(self, task: str) -> Optional[dict[str, Any]]:
        """Best-fit design reference for the task, from the installed
        `design-references` pack. Soft dependency on nx_packs — never fatal."""
        prov = self.registry.get("packs") if self.registry else None
        packs_root = getattr(prov, "packs_dir", None)
        if packs_root is None:
            return None
        try:
            from nx_providers.knowledge import design_refs as _refs
            entries = _refs.installed_references(packs_root)
            top = _refs.match(task, entries, k=1)
            return top[0][0] if top else None
        except Exception:
            return None
