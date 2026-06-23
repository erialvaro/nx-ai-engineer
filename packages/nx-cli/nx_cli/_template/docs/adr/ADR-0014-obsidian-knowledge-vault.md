# ADR-0014: Obsidian as an auto-synced visual representation of the Project Brain

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0013 (Knowledge Providers), ADR-0012 (Autonomous Learning),
  ADR-0004 (Project Brain)

## Context
The Obsidian provider could only *read* a vault. We want Obsidian to be a
**visual representation** of the project's knowledge — a navigable view that
**reflects the Project Brain** and updates automatically on significant changes,
without becoming a second source of truth or duplicating knowledge.

## Decision
Add an **`ObsidianSync`** writer (`knowledge/obsidian_sync.py`) that projects the
current Brain state into an Obsidian vault (default `.ai-project/obsidian/`):
- One note per knowledge **area** in the official numbered structure
  (`00 Dashboard` … `14 Retrospectives` — see ADR-0019). Superseded the original
  flat 12-category layout; Modules/Dependencies are folded into Architecture.
- A **navigation index** (`00 Dashboard/Dashboard.md`, a Map of Content linking every area).
- A **relationship map** (`00 Dashboard/Relationships.md`, a Mermaid graph of ADR references).
- **ADR notes** with auto **backlinks** (`[[ADR-NNNN]]`) between related ADRs.

Guarantees:
- **Reflects the Brain** — it reads the (injected) Brain; it never invents data.
  Obsidian is explicitly **not** the source of truth.
- **No duplication** — notes summarize/link canonical knowledge; ADR bodies are
  linked (by source path), not copied; each fact lives in one category note.
- **Incremental** — a manifest (`.aies-sync.json`) tracks note hashes; only
  changed notes are written and orphaned AIES notes are pruned. **User notes are
  never touched** (only manifest-tracked, `aies-generated` notes are managed).
- **Automatic** — `attach(bus)` re-syncs on `pipeline.completed` / `adr.created`.
  Controlled by `config.obsidian_sync` (default on); writes are best-effort and
  never break a run.

The Brain is **injected** (duck-typed), so the knowledge layer still never
imports Memory — no cycle. New CLI: `obsidian sync|status`.

## Alternatives considered
- **Make the vault writable / a source of truth.** Rejected: the prompt requires
  Obsidian to reflect the Brain, not own it; round-tripping edits would create a
  second source of truth.
- **Copy ADR/doc bodies into notes.** Rejected: duplication. We link/summarize.
- **Re-render the whole vault every time.** Rejected: not incremental. The
  manifest makes writes minimal.
- **Sync on every `brain.updated`.** Rejected: too chatty (the Brain bumps often
  per run). We sync on `pipeline.completed` / `adr.created` (significant changes).

## Consequences
- After each pipeline run (or ADR creation), `.ai-project/obsidian/` mirrors the
  Brain: navigable, backlinked, with a relationship graph — openable in Obsidian.
- The Obsidian **provider** (reader) defaults to this generated vault, closing
  the loop (the platform can re-read what it rendered).
- Backward compatible and additive. Covered by `test_obsidian_sync.py`
  (categories, index, backlinks, relationship map, incremental, no-duplication,
  auto-sync, config gate). Full suite green; no cycles (quality gate enforces).
