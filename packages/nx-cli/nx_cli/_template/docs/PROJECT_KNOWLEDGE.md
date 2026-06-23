# Project Knowledge Engine — Doctrine

This document defines, and bounds, what the Project Knowledge Engine is — and
what it is **not**. It is a guardrail: the architecture and tests enforce it.

## What it is NOT
- It does **not** learn programming.
- It does **not** improve AI models.
- It does **not** create reasoning mechanisms.

**All intelligence belongs to the AI model.** The Knowledge Engine adds none.

## The five (and only five) responsibilities
| # | Responsibility | Method | Backed by |
|---|----------------|--------|-----------|
| 1 | **Discover** existing knowledge | `discover()` | Knowledge Providers scan the sources |
| 2 | **Index** knowledge | `index()` | the registry's retrievable catalog |
| 3 | **Relate** knowledge | `relate()` | the automatic Knowledge Graph |
| 4 | **Update** knowledge | `update()` | sync of the three memories (Brain/Obsidian/Git) |
| 5 | **Deliver enriched context** to agents | `deliver_context(paths)` | graph-related elements added to `AgentContext` |

```python
from nx_knowledge.knowledge.engine import KnowledgeEngine
eng = KnowledgeEngine(brain, config=cfg)
eng.discover()                       # 1
eng.index()                          # 2
eng.relate()                         # 3
eng.update()                         # 4
eng.deliver_context(context_files)   # 5
```

## The principle
The engine only **reduces the model's cognitive load**. It never reasons or
answers. The economics follow directly:

> The larger the project history → the richer the context → the more assertive
> the implementation → the **fewer tokens** consumed.

`knowledge status` surfaces this as **context richness** (graph nodes/edges),
which grows as the project's history grows.

## How it is enforced
- The `aies/knowledge/` layer may import **only** `foundation` and `agents`
  (data/primitives) — never `intelligence`, `schedulers`, `evolution`, `kernel`,
  `memory`, `governance`, etc. A test (`test_knowledge_doctrine.py`) fails the
  build if any reasoning layer is imported.
- Providers and the graph return **only structured data** (paths, names, counts,
  relationships) — never decisions, code interpretation, or generated prose.
- `KnowledgeEngine.RESPONSIBILITIES` lists exactly the five methods; a test
  asserts the contract.

See also: `KNOWLEDGE_GUIDE.md`, ADR-0013 (Providers), ADR-0015 (Engine/three
memories), ADR-0017 (Graph), ADR-0018 (this doctrine).
