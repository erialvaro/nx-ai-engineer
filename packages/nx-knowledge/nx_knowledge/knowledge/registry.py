"""Knowledge Registry — the single entry point to all Knowledge Providers.

Nothing consumes a knowledge source directly; everything goes through this
registry. New providers (e.g. Confluence, Notion, a vector store) register here
without touching the Context Engine.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from nx_core.foundation import util
from nx_providers.knowledge.adr import ADRProvider
from nx_providers.knowledge.base import KnowledgeItem, KnowledgeProvider, Relationship
from nx_providers.knowledge.filesystem import FilesystemProvider
from nx_providers.knowledge.git import GitProvider
from nx_providers.knowledge.markdown import MarkdownProvider
from nx_obsidian.knowledge.obsidian import ObsidianProvider
from nx_providers.knowledge.packs import PackProvider
from nx_providers.knowledge.project_brain import ProjectBrainProvider


class KnowledgeRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, KnowledgeProvider] = {}

    def register(self, provider: KnowledgeProvider) -> KnowledgeProvider:
        self._providers[provider.name] = provider
        return provider

    def get(self, name: str) -> Optional[KnowledgeProvider]:
        return self._providers.get(name)

    def providers(self) -> list[KnowledgeProvider]:
        return list(self._providers.values())

    def names(self) -> list[str]:
        return sorted(self._providers)

    def index_all(self) -> dict[str, int]:
        return {p.name: p.index() for p in self._providers.values()}

    def catalog(self) -> list[KnowledgeItem]:
        out: list[KnowledgeItem] = []
        for p in self._providers.values():
            try:
                out.extend(p.catalog())
            except Exception:
                pass  # a misbehaving provider must not break the platform
        return out

    def retrieve(self, scope: Optional[dict[str, Any]] = None,
                 providers: Optional[list[str]] = None) -> list[KnowledgeItem]:
        out: list[KnowledgeItem] = []
        for p in self._providers.values():
            if providers and p.name not in providers:
                continue
            try:
                out.extend(p.retrieve(scope))
            except Exception:
                pass
        return out

    def relationships(self) -> list[Relationship]:
        out: list[Relationship] = []
        for p in self._providers.values():
            try:
                out.extend(p.relationships())
            except Exception:
                pass
        return out


def default_registry(*, root: Optional[Path] = None, config: Optional[dict] = None,
                     brain: Any = None) -> KnowledgeRegistry:
    """Build the standard set of providers. `brain` is injected (duck-typed) so
    this layer never imports the Memory layer; pass `None` to omit it."""
    reg = KnowledgeRegistry()
    reg.register(FilesystemProvider(root, config=config))
    reg.register(GitProvider(root))
    reg.register(MarkdownProvider(root))
    reg.register(ADRProvider(root))
    reg.register(ObsidianProvider(root, config=config))
    # Packs live in the data home (.ai-project-assistant/packs), not the project source root.
    reg.register(PackProvider(util.config_root()))
    if brain is not None:
        reg.register(ProjectBrainProvider(brain))
    return reg
