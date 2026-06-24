# Provider SDK Guide

A **Knowledge Provider** is how NX AI Engineer brings a knowledge source into the
platform. Nothing consumes a source directly — the Context Engine retrieves
through the **Knowledge Registry**, which is a set of providers. Add a provider
and your source becomes available to every agent's context, with **zero changes to
the core** (Open/Closed).

## The contract

A provider implements `nx_providers.knowledge.base.KnowledgeProvider`:

| Method | Responsibility |
|---|---|
| `index() -> int` | (re)build the catalog; return the item count |
| `catalog() -> list[KnowledgeItem]` | all known items (structured) |
| `retrieve(scope) -> list[KnowledgeItem]` | pure filter + order by relevance (provided by the base) |
| `enrich(item) -> KnowledgeItem` | add metadata (optional; default no-op) |
| `relationships() -> list[Relationship]` | relate items (default: from items) |

A provider's **only** job is to organize knowledge. By doctrine it MUST NOT:

- make decisions (that is the Decision/Intelligence layer),
- interpret code (it surfaces metadata/paths, not parsed semantics),
- generate answers (it returns **data**, not prose).

It is a pure, read-only knowledge source. Stdlib-only in the core; your own
provider may use anything.

## Data shapes

```python
from nx_providers.knowledge.base import KnowledgeItem, Relationship

KnowledgeItem(
    id="doc:guide",          # stable id
    provider="my-source",
    kind="doc",              # file | commit | doc | adr | note | pack | brain-* | …
    ref="path/or/identifier",
    title="Human title",
    metadata={"any": "structured data"},
    relationships=[Relationship("doc:guide", "doc:other", "links-to")],
)
```

## Writing a provider

```python
from nx_providers.knowledge.base import KnowledgeItem, KnowledgeProvider

class MySourceProvider(KnowledgeProvider):
    name = "my-source"

    def __init__(self, root=None):
        self.root = root
        self._items = None

    def index(self):
        self._items = self._scan()
        return len(self._items)

    def catalog(self):
        if self._items is None:
            self._items = self._scan()
        return self._items

    def _scan(self):
        # read your source; return structured KnowledgeItems (no decisions/prose)
        return [KnowledgeItem(id="my:1", provider=self.name, kind="doc",
                              ref="…", title="…", metadata={...})]
```

`retrieve()` is implemented by the base (pure token/area scoring) — you usually
only implement `index()` + `catalog()`. The built-in providers
(`filesystem`, `git`, `markdown`, `adr`, `obsidian`, `project-brain`, `packs`) are
worked examples to copy.

## Registering it

Register at startup through the SDK (no core change):

```python
import nx_sdk as sdk
sdk.register_provider  # via a plugin's setup(sdk) or your own bootstrap
```

…or, in a custom build of the registry, add `reg.register(MySourceProvider(root))`.
A **plugin** is the packaged way to ship one or more providers/agents/engines —
see the [Plugin Guide](PLUGIN_GUIDE.md) and [SDK Guide](SDK_GUIDE.md).

## Engineering Packs are a provider, too

The **Pack Provider** (`nx_providers.knowledge.packs.PackProvider`) catalogs the
Engineering Packs installed under `.ai-project-assistant/packs/`. Authoring a pack is the
no-code way to add domain knowledge — see the [Packs Guide](PACKS_GUIDE.md). To
ship packs to others, follow the catalog convention in the
[Marketplace](MARKETPLACE.md).

## Guarantees

- Registering a provider never mutates the core; the registry composes providers.
- A misbehaving provider can never break the platform (the registry isolates each).
- Providers return **structured data**, never decisions or generated prose.
