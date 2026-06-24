# ADR-0003: Context Engine — minimal, ranked, cached per-agent context

- **Status:** Accepted
- **Date:** 2026-06-21
- **Sprint:** AIES 3.0 — S1 (PR-4)

## Context
Feeding an agent the whole repository is expensive and noisy. Each agent should
receive only what is relevant to its subtask. We need this to be deterministic,
offline, stdlib-only, and cheap to recompute.

## Decision
1. Add a **Context Engine** (`memory/context.py`) with a `ContextBuilder` that
   runs pluggable **resolvers** — Files, Services, APIs, Tests, Docs and
   Dependencies — over the project file list.
2. Each resolver returns ranked items; relevance combines agent **ownership**
   (route globs), **subtask area** proximity and **name/keyword** overlap. The
   builder keeps the top-N per category and assembles a minimal `AgentContext`.
3. Report an **estimated context reduction** (fraction of the repo omitted) and
   publish it via `context.built`.
4. **Cache** results (`memory/cache.py`, under `.ai-project-assistant/context-cache/`).
   The cache key embeds a **version** (git HEAD, or a file-mtime signature when
   not a repo), so a changed project yields a new key — invalidation is by
   construction.

## Alternatives considered
- **Send the whole repo / a fixed file glob.** Rejected: defeats the purpose and
  scales badly.
- **Embeddings / vector similarity now.** Deferred to the Semantic Knowledge
  layer (PR-5 stub, full impl later); it requires dependencies we avoid in core.
- **mtime-diff cache invalidation.** Replaced by version-in-key, which is simpler
  and race-free.

## Consequences
- New CLI command: `orchestrator.py context --plan <id> --agent <a> [--no-cache]`
  showing the minimal context and the reduction percentage.
- Resolvers are pluggable; new ones (or a `SemanticResolver`) can be added via the
  SDK without touching the builder.
- Backward compatible and additive; covered by the context test suite (resolvers,
  ranking, cache hit, reduction range, event emission).
- The unified pipeline (PR-7) will call the Context Engine before dispatching
  each agent.
