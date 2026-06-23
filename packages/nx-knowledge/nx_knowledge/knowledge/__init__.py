"""Knowledge aggregate — re-exports the knowledge API across the split packages.

The knowledge layer is physically split into nx-providers (the source providers),
nx-obsidian (the Obsidian provider/sync) and nx-knowledge (engine/graph/registry).
This module re-assembles the original `knowledge` public surface so existing
imports (`from aies.knowledge import ...`, mapped here) keep working.
"""
from nx_providers.knowledge.adr import ADRProvider
from nx_providers.knowledge.base import (
    KnowledgeItem, KnowledgeProvider, Relationship,
)
from nx_providers.knowledge.filesystem import FilesystemProvider
from nx_providers.knowledge.git import GitProvider
from nx_providers.knowledge.markdown import MarkdownProvider
from nx_providers.knowledge.project_brain import ProjectBrainProvider
from nx_obsidian.knowledge.obsidian import ObsidianProvider
from nx_obsidian.knowledge.obsidian_sync import ObsidianSync

from .engine import KnowledgeEngine
from nx_providers.knowledge.graph import GraphEdge, GraphNode, KnowledgeGraph, KnowledgeGraphBuilder
from .registry import KnowledgeRegistry, default_registry

__all__ = [
    "KnowledgeItem", "KnowledgeProvider", "Relationship",
    "FilesystemProvider", "GitProvider", "MarkdownProvider", "ADRProvider",
    "ProjectBrainProvider", "ObsidianProvider", "ObsidianSync",
    "KnowledgeRegistry", "default_registry", "KnowledgeEngine",
    "KnowledgeGraph", "KnowledgeGraphBuilder", "GraphNode", "GraphEdge",
]
