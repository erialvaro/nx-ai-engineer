"""Obsidian Sync — render the Project Brain as a navigable Obsidian vault.

Obsidian is a **visual representation** of the project's knowledge — never the
source of truth. This writer projects the current Project Brain state (plus ADRs)
into the official numbered vault structure (``00 Dashboard`` … ``14
Retrospectives``): one folder per knowledge area with an index note, a Dashboard
(navigation + Map of Content), a relationship map, and ADR notes with backlinks.

Principles:
- **Reflects the Brain**: it reads the (injected) Brain — it never invents data.
- **No duplication**: notes summarize/link canonical knowledge; ADR bodies are
  not copied (they are linked), and each fact lives in exactly one area note.
- **Incremental**: a manifest tracks note hashes; only changed notes are written,
  and AIES-generated notes that disappear are pruned. User notes are never touched.
- **Automatic**: `attach(bus)` re-syncs on significant changes (pipeline.completed
  / adr.created).

The Brain is injected (duck-typed: get/read_log/version) so this module never
imports the Memory layer — keeping the dependency graph acyclic.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util
from nx_providers.knowledge.adr import ADRProvider
from .obsidian import default_vault

MANIFEST = ".aies-sync.json"

# The official vault structure: (folder, note title). The numbered folders are the
# product's canonical Obsidian layout; the note title is the wikilink target.
VAULT: list[tuple[str, str]] = [
    ("00 Dashboard", "Dashboard"),
    ("01 Architecture", "Architecture"),
    ("02 ADR", "ADRs"),
    ("03 Decisions", "Decisions"),
    ("04 Features", "Features"),
    ("05 APIs", "APIs"),
    ("06 Services", "Services"),
    ("07 Database", "Database"),
    ("08 Workflows", "Workflows"),
    ("09 Bugs", "Bugs"),
    ("10 Lessons Learned", "Lessons Learned"),
    ("11 Roadmap", "Roadmap"),
    ("12 Releases", "Releases"),
    ("13 Metrics", "Metrics"),
    ("14 Retrospectives", "Retrospectives"),
]
# Note titles, in order — drives the Dashboard Map of Content + coverage.
CATEGORIES = [title for _folder, title in VAULT]
_FOLDER = {title: folder for folder, title in VAULT}


def _path(title: str) -> str:
    """Vault-relative note path for a category title (e.g. '01 Architecture/Architecture.md')."""
    return f"{_FOLDER[title]}/{title}.md"


def _fm(category: str) -> str:
    # Frontmatter WITHOUT a timestamp, so unchanged data => identical content =>
    # the note is not rewritten (true incremental sync).
    return f"---\naies-generated: true\ncategory: {category}\n---\n"


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", str(text)) or "x"


class ObsidianSync:
    name = "obsidian-sync"

    def __init__(self, brain: Any, *, vault: Optional[Path] = None,
                 config: Optional[dict] = None, root: Optional[Path] = None,
                 bus=None) -> None:
        self.brain = brain
        self.config = config or {}
        self.root = root or util.project_root()
        self.vault = Path(vault) if vault else default_vault(self.config)
        self._adr = ADRProvider(self.root)
        self._bus = None
        if bus is not None:
            self.attach(bus)

    # -- automatic sync --------------------------------------------------- #
    def attach(self, bus) -> None:
        self._bus = bus
        bus.subscribe("pipeline.completed", self._on_change)
        bus.subscribe("adr.created", self._on_change)

    def _on_change(self, _event) -> None:
        if self.config.get("obsidian_sync", True):
            try:
                self.sync()
            except Exception:
                pass  # representation is best-effort; never break a run

    # -- the sync --------------------------------------------------------- #
    def sync(self) -> dict[str, Any]:
        notes = self._render_all()
        report = self._write_incremental(notes)
        if self._bus is not None:
            self._bus.emit("obsidian.synced", report)
        return report

    def _render_all(self) -> dict[str, str]:
        notes: dict[str, str] = {}
        notes[_path("Dashboard")] = self._render_dashboard()
        notes["00 Dashboard/Relationships.md"] = self._render_relationships()
        notes[_path("Architecture")] = self._render_architecture()
        adrs_idx, adr_notes = self._render_adrs()
        notes[_path("ADRs")] = adrs_idx
        for name, content in adr_notes.items():
            notes[f"02 ADR/{name}"] = content
        notes[_path("Decisions")] = self._render_log("Decisions", "decisions", ("ADRs",))
        notes[_path("Features")] = self._render_features()
        notes[_path("APIs")] = self._render_facet("APIs", "apis", ("Services", "Architecture"))
        notes[_path("Services")] = self._render_facet("Services", "services", ("APIs", "Architecture"))
        notes[_path("Database")] = self._render_facet("Database", "database", ("Services", "Architecture"))
        notes[_path("Workflows")] = self._render_workflows()
        notes[_path("Bugs")] = self._render_log("Bugs", "bugs", ("Lessons Learned",))
        notes[_path("Lessons Learned")] = self._render_lessons()
        notes[_path("Roadmap")] = self._render_roadmap()
        notes[_path("Releases")] = self._render_releases()
        notes[_path("Metrics")] = self._render_metrics()
        notes[_path("Retrospectives")] = self._render_retros()
        return notes

    # -- incremental writer ---------------------------------------------- #
    def _write_incremental(self, notes: dict[str, str]) -> dict[str, Any]:
        util.ensure_dir(self.vault)
        util.ensure_dir(self.vault / ".obsidian")  # make it a real vault
        manifest = util.read_json(self.vault / MANIFEST, {"notes": {}}) or {"notes": {}}
        old = manifest.get("notes", {})
        new: dict[str, str] = {}
        written = unchanged = 0

        for name, content in notes.items():
            sha = util.short_hash(content, 16)
            new[name] = sha
            path = self.vault / name
            if old.get(name) == sha and path.exists():
                unchanged += 1
                continue
            util.write_text(path, content)  # creates parent folders as needed
            written += 1

        removed = 0
        for name in old:
            if name not in new:
                p = self.vault / name
                if p.exists():
                    try:
                        p.unlink()
                        removed += 1
                    except OSError:
                        pass

        util.write_json(self.vault / MANIFEST,
                        {"notes": new, "synced_at": util.now_iso(),
                         "brain_version": self._brain_version(), "count": len(new)})
        return {"written": written, "unchanged": unchanged, "removed": removed,
                "total": len(new), "vault": str(self.vault)}

    # -- renderers (read-only over the Brain) ---------------------------- #
    def _render_dashboard(self) -> str:
        L = [_fm("Dashboard"), "# 🧠 Project Knowledge — Dashboard",
             "", "_A visual reflection of the Project Brain. Not the source of "
             "truth — it mirrors the Brain and updates automatically._", "",
             "## Map of Content"]
        for folder, title in VAULT:
            if title == "Dashboard":
                continue
            L.append(f"- **{folder.split(' ', 1)[0]}** · [[{title}]]")
        L += ["", "## Maps", "- [[Relationships]]",
              "", f"> Brain version: {self._brain_version()}"]
        return "\n".join(L) + "\n"

    def _related(self, names) -> str:
        return "\n".join(["", "---", "**Related:** " + " · ".join(
            f"[[{n}]]" for n in ("Dashboard", *names))]) + "\n"

    def _render_adrs(self) -> tuple[str, dict[str, str]]:
        items = self._adr.catalog()
        idx = [_fm("ADRs"), "# Architecture Decision Records", ""]
        detail: dict[str, str] = {}
        if not items:
            idx.append("_No ADRs found._")
        for it in items:
            num = it.metadata.get("number", 0)
            note = f"ADR-{num:04d}"
            idx.append(f"- [[{note}]] — {it.title}  ·  _{it.metadata.get('status', '?')}_")
            body = [_fm("ADRs"), f"# {it.title}", "",
                    f"- **Number:** {num}", f"- **Status:** {it.metadata.get('status', '?')}",
                    f"- **Source:** `{it.ref}`", ""]
            refs = [r.target for r in it.relationships if r.kind == "references"]
            if refs:
                body.append("**References:** " + " · ".join(
                    f"[[ADR-{int(t.split(':')[-1]):04d}]]" for t in refs))
            body.append(self._related(("ADRs",)))
            detail[f"{note}.md"] = "\n".join(body) + "\n"
        return "\n".join(idx) + self._related(("Decisions", "Relationships")), detail

    def _render_architecture(self) -> str:
        arch = self._get("architecture", "current") or {}
        L = [_fm("Architecture"), "# Architecture", ""]
        if arch:
            L += [f"- **Stacks:** {', '.join(arch.get('stacks', [])) or '—'}",
                  f"- **Frameworks:** {', '.join(arch.get('frameworks', [])) or '—'}",
                  f"- **Monorepo:** {arch.get('is_monorepo', False)}",
                  f"- **Top-level dirs:** {', '.join(arch.get('top_level_dirs', [])[:12]) or '—'}"]
            langs = arch.get("languages", {})
            if langs:
                L.append("- **Languages:** " + ", ".join(f"{k}({v})" for k, v in list(langs.items())[:8]))
        else:
            L.append("_Run `audit` to populate architecture knowledge._")
        # Modules + Dependencies live here (folded into Architecture).
        modules = self._get("modules") or {}
        L += ["", "## Modules"]
        L += [f"- **{k}**" for k in sorted(modules)] or ["_None recorded yet._"]
        deps = self._get("dependencies") or {}
        fw = arch.get("frameworks", [])
        L += ["", "## Dependencies"]
        if fw:
            L += [f"- {f} _(framework)_" for f in fw]
        if deps:
            L += [f"- **{k}** — {v}" for k, v in sorted(deps.items())]
        if not fw and not deps:
            L.append("_None recorded yet — run `audit`._")
        return "\n".join(L) + self._related(("Services", "APIs", "Database", "Relationships"))

    def _render_roadmap(self) -> str:
        # Roadmap is maintained as a canonical doc — link, never duplicate.
        L = [_fm("Roadmap"), "# Roadmap", "",
             "_The roadmap is maintained in the project's `ROADMAP.md` "
             "(canonical). This note links to it to avoid duplication._", "",
             "- Source: `ROADMAP.md`"]
        return "\n".join(L) + self._related(("Features", "Releases"))

    def _render_releases(self) -> str:
        L = [_fm("Releases"), "# Releases", "",
             "_Canonical release history lives in `CHANGELOG.md` / "
             "`RELEASE_NOTES.md`. This note links to them and shows the current "
             "knowledge version._", "",
             "- Source: `CHANGELOG.md`, `RELEASE_NOTES.md`",
             f"- Project Brain version: **{self._brain_version()}**"]
        try:
            import nx_core
            L.append(f"- Platform version: **{getattr(nx_core, '__version__', '?')}**")
        except Exception:
            pass
        return "\n".join(L) + self._related(("Roadmap", "Metrics"))

    def _render_metrics(self) -> str:
        retros = self._log("retrospectives")
        total = len(retros)
        ok = sum(1 for r in retros if r.get("strategy_success") is not False
                 and int(r.get("failures", 0)) == 0)
        L = [_fm("Metrics"), "# Metrics", "",
             "_Operational KPIs derived from the Brain. Full telemetry via "
             "`nxai metrics`._", "",
             f"- **Runs recorded:** {total}",
             f"- **Clean runs:** {ok}" + (f" ({ok * 100 // total}%)" if total else ""),
             f"- **Workflows tracked:** {len(self._get('workflows') or {})}",
             f"- **Knowledge entries:** {len(self._log('knowledge'))}"]
        return "\n".join(L) + self._related(("Workflows", "Retrospectives", "Releases"))

    def _render_workflows(self) -> str:
        data = self._get("workflows") or {}
        L = [_fm("Workflows"), "# Workflows", ""]
        if data:
            for key in sorted(data):
                rec = data[key]
                meta = ", ".join(f"{k}={v}" for k, v in rec.items() if k != "_updated") \
                    if isinstance(rec, dict) else str(rec)
                L.append(f"- **{key}** — {meta}")
        else:
            L.append("_No workflow statistics recorded yet — they accrue per run._")
        return "\n".join(L) + self._related(("Metrics", "Retrospectives"))

    def _render_features(self) -> str:
        # Features are inferred from the goals worked on (retrospectives).
        seen, rows = set(), []
        for r in self._log("retrospectives"):
            req = (r.get("request") or "").strip()
            if req and req.lower() not in seen:
                seen.add(req.lower())
                rows.append(f"- {req}  ·  _{r.get('status', '?')}_")
        L = [_fm("Features"), "# Features", ""]
        L += rows or ["_No features recorded yet — populated as goals are run._"]
        return "\n".join(L) + self._related(("Retrospectives", "Roadmap"))

    def _render_facet(self, title: str, facet: str, related) -> str:
        data = self._get(facet) or {}
        L = [_fm(title), f"# {title}", ""]
        if data:
            for key in sorted(data):
                rec = data[key]
                meta = ", ".join(f"{k}={v}" for k, v in rec.items() if k != "_updated") \
                    if isinstance(rec, dict) else str(rec)
                L.append(f"- **{key}** — {meta}")
        else:
            L.append(f"_No {title.lower()} recorded in the Brain yet._")
        return "\n".join(L) + self._related(related)

    def _render_log(self, title: str, facet: str, related) -> str:
        rows = self._log(facet)
        L = [_fm(title), f"# {title}", ""]
        if rows:
            for r in rows[-30:][::-1]:
                summary = ", ".join(f"{k}={v}" for k, v in r.items()
                                    if k not in ("id", "ts") and v is not None)
                L.append(f"- {summary}")
        else:
            L.append(f"_No {title.lower()} recorded yet._")
        return "\n".join(L) + self._related(related)

    def _render_retros(self) -> str:
        rows = self._log("retrospectives")
        L = [_fm("Retrospectives"), "# Retrospectives", ""]
        if rows:
            for r in rows[-20:][::-1]:
                L.append(
                    f"- **{(r.get('request') or '')[:60]}** — "
                    f"{r.get('status')} · wf={r.get('workflow')} · "
                    f"agents={','.join(r.get('agents_used', []) or [])} · "
                    f"retries={r.get('retries', 0)} · success={r.get('strategy_success')}")
        else:
            L.append("_No retrospectives yet._")
        return "\n".join(L) + self._related(("Lessons Learned", "Decisions"))

    def _render_lessons(self) -> str:
        L = [_fm("Lessons Learned"), "# Lessons Learned", ""]
        lessons = []
        for r in self._log("retrospectives"):
            if int(r.get("failures", 0)) > 0 or r.get("strategy_success") is False:
                lessons.append(
                    f"- On **{(r.get('request') or '')[:50]}**: "
                    f"{r.get('failures', 0)} failure(s), {r.get('retries', 0)} retr(y/ies) "
                    f"with {','.join(r.get('agents_used', []) or [])} — review the approach.")
        for k in self._log("knowledge")[-10:]:
            lessons.append(f"- Review knowledge: {', '.join(f'{a}={b}' for a, b in k.items() if a not in ('id', 'ts'))}")
        L += lessons or ["_No lessons recorded yet — they accrue from failures/reviews._"]
        return "\n".join(L) + self._related(("Retrospectives", "Bugs"))

    def _render_relationships(self) -> str:
        items = self._adr.catalog()
        edges = []
        for it in items:
            a = f"ADR{it.metadata.get('number', 0):04d}"
            for r in it.relationships:
                if r.kind == "references":
                    edges.append((a, f"ADR{int(r.target.split(':')[-1]):04d}"))
        L = [_fm("Relationships"), "# Relationship Map", "",
             "_Auto-generated graph of how knowledge connects (ADR references)._", ""]
        if edges:
            L.append("```mermaid\ngraph TD")
            for src, dst in edges[:60]:
                L.append(f"  {src}[\"{src}\"] --> {dst}[\"{dst}\"]")
            L.append("```")
            L += ["", "## ADR Edges"] + [f"- [[ADR-{s[3:]}]] → [[ADR-{d[3:]}]]" for s, d in edges[:60]]
        else:
            L.append("_No ADR relationships discovered yet._")

        # The full element graph (Service→API→DB→Test→Bug→Feature→…) from the Brain.
        try:
            from nx_providers.knowledge.graph import KnowledgeGraphBuilder
            g = KnowledgeGraphBuilder(self.brain).build()
            if g.edges:
                L += ["", "## Element graph", "",
                      f"_{g.stats()['nodes']} elements, {g.stats()['edges']} relationships._",
                      "", g.to_mermaid(60)]
        except Exception:
            pass
        return "\n".join(L) + self._related(("ADRs",))

    # -- defensive Brain accessors --------------------------------------- #
    def _get(self, facet: str, key: str | None = None):
        try:
            return self.brain.get(facet, key) if key is not None else self.brain.get(facet)
        except Exception:
            return None

    def _log(self, facet: str):
        try:
            return self.brain.read_log(facet)
        except Exception:
            return []

    def _brain_version(self) -> int:
        try:
            return int(self.brain.version())
        except Exception:
            return 0
