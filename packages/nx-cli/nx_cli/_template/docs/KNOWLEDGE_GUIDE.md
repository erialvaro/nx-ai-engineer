# Knowledge Providers Guide

> **Doctrine** (see [PROJECT_KNOWLEDGE.md](PROJECT_KNOWLEDGE.md)): the Project
> Knowledge Engine has exactly five responsibilities — **discover, index, relate,
> update, deliver enriched context** — and **no reasoning**. All intelligence
> belongs to the AI model; the engine only reduces its cognitive load.

AIES uses a **Knowledge Provider** architecture. No knowledge source is coupled
directly to the Context Engine — every source goes through a provider, and the
Context Engine retrieves through the **Knowledge Engine**.

> See ADR-0013 (providers) and ADR-0015 (Knowledge Engine). The Context Engine
> consumes the Knowledge Engine; it never walks the filesystem or queries
> git/brain directly.

## The three memories (Knowledge Engine)
The **Knowledge Engine** (`aies.knowledge.engine.KnowledgeEngine`) is the single
coordination + access point. It unifies and synchronizes the three memories:

| Memory | Role | Backed by |
|--------|------|-----------|
| **Project Brain** | operational (current state) | `.ai-project/brain/` |
| **Obsidian** | organizational (navigable view) | `.ai-project/obsidian/` |
| **Git** | historical (immutable record) | the repository |

Canonical flow:
```
Project Brain → Knowledge Engine → Knowledge Providers → Obsidian
              → Context Engine → Agents
```
```python
from nx_knowledge.knowledge.engine import KnowledgeEngine
eng = KnowledgeEngine(brain, config=cfg)
eng.retrieve({"query": "auth"})     # access point used by the Context Engine
eng.sync(commit=False)              # Obsidian ← Brain; (opt-in) snapshot → Git
eng.status()                        # alignment of the three memories
```
CLI: `knowledge sync [--commit]` · `knowledge status`. The engine auto-syncs on
`pipeline.completed` / `adr.created`. Git snapshotting is **opt-in**
(`--commit` / `config.knowledge_git_snapshot`); status reads Git read-only.

## Knowledge Graph (automatic relationships)
The Knowledge Engine builds a **typed graph** connecting project elements —
`Service → API → Database → Migration → Test → ADR → Bug → Feature → Sprint →
Documentation → Obsidian`. Edges are **inferred automatically** (never by reading
code): co-occurrence in one execution (Project Evolution records), bugs→features,
sprints→features, ADR references, doc links.
```python
eng.graph()                                   # KnowledgeGraph (cached; rebuilt on sync)
eng.enrich_context(["apps/api/services/x.py"]) # related {api, test, entity, adr, bug, …}
```
The graph is used **only to enrich** the context handed to agents (the Context
Engine adds related APIs/tests/services/docs/ADRs/bugs to `AgentContext`). It
returns only data — **it never decides, interprets code or replaces the model's
reasoning**. CLI: `knowledge graph [--format summary|mermaid|json] [--query <path>]`.

## What a provider is
A `KnowledgeProvider` (in `aies.knowledge.base`) supplies **structured
knowledge** and nothing else. It can:
- **index** — build/refresh its catalog,
- **catalog** — list what it knows as `KnowledgeItem`s,
- **retrieve** — return items relevant to a scope (`{query, areas, limit}`),
- **enrich** — add metadata to an item,
- **relationships** — relate items to each other.

A provider **must never**: make decisions, interpret code, or generate answers.
It is a pure, read-only knowledge source.

### `KnowledgeItem`
```python
KnowledgeItem(id, provider, kind, ref, title, metadata={}, relationships=[])
# kind ∈ {file, commit, change, doc, adr, note, brain-pattern, brain-workflow, …}
```
Relationships are `Relationship(source, target, kind)` (links-to, references,
wikilink, …).

## Built-in providers
| Provider | Surfaces | Relationships |
|----------|----------|---------------|
| **filesystem** | files (path, ext, language, owner agent, size) | — |
| **git** | commits (author/date/subject), changed files | change → file |
| **markdown** | doc title, heading outline, word count | links-to (other docs) |
| **adr** | ADR number, title, status | references (other ADRs) |
| **project-brain** | learned patterns, workflow stats, retrospectives | — |
| **obsidian** | notes, tags, `[[wikilinks]]` | wikilink |

> The Filesystem provider surfaces file *metadata* only — it never opens code.
> The Project-Brain provider is injected with a Brain instance (the knowledge
> layer never imports Memory), keeping dependencies acyclic.

## Registry
```python
from nx_knowledge.knowledge import default_registry
reg = default_registry(config=cfg, brain=brain)   # brain optional
reg.index_all()                                    # {provider: count}
reg.catalog()                                      # all items
reg.retrieve({"query": "auth"}, providers=["markdown", "adr"])
reg.relationships()                                # all edges
```

## CLI
```
orchestrator.py knowledge index
orchestrator.py knowledge list --provider markdown
orchestrator.py knowledge retrieve --query "oauth" --provider adr --limit 10
```

## How the Context Engine uses providers
- The **file list** comes from the `FilesystemProvider` (`.paths()` / `.version()`).
- **Docs** are enriched from the Markdown + ADR providers.
- **Patterns** are enriched from the Project-Brain provider.
- Resolvers then rank these into the minimal `AgentContext`.

## Obsidian — a visual representation of the Brain (auto-synced)

Obsidian is a **view**, never the source of truth. `ObsidianSync`
(`knowledge/obsidian_sync.py`) projects the current Project Brain into a vault
(default `.ai-project/obsidian/`):
- the official numbered structure — folders `00 Dashboard`, `01 Architecture`,
  `02 ADR`, `03 Decisions`, `04 Features`, `05 APIs`, `06 Services`,
  `07 Database`, `08 Workflows`, `09 Bugs`, `10 Lessons Learned`, `11 Roadmap`,
  `12 Releases`, `13 Metrics`, `14 Retrospectives` (Modules/Dependencies are
  folded into Architecture);
- a navigation index (`00 Dashboard/Dashboard.md`, Map of Content);
- a relationship map (`00 Dashboard/Relationships.md`, Mermaid graph of ADR references);
- ADR notes with auto `[[backlinks]]`.

It **reflects the Brain** (never invents data), is **incremental** (a manifest
writes only changed notes and prunes orphans; user notes are never touched),
avoids **duplication** (links/summaries, no copied bodies), and syncs
**automatically** on `pipeline.completed` / `adr.created` (config
`obsidian_sync`, default on). CLI:
```
orchestrator.py obsidian sync       # render the vault now (incremental)
orchestrator.py obsidian status     # vault path, note count, last sync
```
The Obsidian **provider** (reader) defaults to this generated vault.

## Adding a provider
Implement `KnowledgeProvider` (`index` + `catalog`; inherit `retrieve`/`enrich`/
`relationships` or override). Register it:
```python
from nx_knowledge.knowledge import KnowledgeRegistry
reg = KnowledgeRegistry()
reg.register(MyConfluenceProvider())
```
Keep it pure: structured knowledge only — no decisions, no code interpretation,
no generated prose. A runnable example pattern lives in `examples/` (adapt
`04_create_adapter.py`'s injection style).
