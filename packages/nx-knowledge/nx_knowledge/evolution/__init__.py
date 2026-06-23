"""Autonomous Learning — the layer that makes AIES evolve from its own use.

After each pipeline run the platform learns (time, failures, rework, agents,
files changed, recurring patterns, decisions, strategy success) and updates the
Project Brain automatically. It stores **knowledge, never code**, and reuses the
existing Memory/Experience/Semantic infrastructure.

Components:
- ExperienceAnalyzer  — aggregates KPIs/trends from the Brain.
- PatternDiscovery    — mines recurring patterns (agent sets, failure-prone).
- SimilarTaskDetector — finds similar past tasks (reuses the Semantic index).
- RecommendationEngine— recommends agents/workflow from what worked before.
- KnowledgeEvolution  — incremental, versioned consolidation into the Brain.
- BrainOptimizer      — compacts/bounds the Brain.
- SelfImprovementEngine — orchestrates all of the above per execution.
"""
from .brain_optimizer import BrainOptimizer
from .experience_analyzer import ExperienceAnalyzer
from .knowledge_evolution import KnowledgeEvolution
from .pattern_discovery import PatternDiscovery
from .project_evolution import ProjectEvolutionEngine
from .recommendation import RecommendationEngine
from .self_improvement import SelfImprovementEngine
from .similarity import SimilarTaskDetector

__all__ = [
    "ExperienceAnalyzer", "PatternDiscovery", "SimilarTaskDetector",
    "RecommendationEngine", "KnowledgeEvolution", "BrainOptimizer",
    "ProjectEvolutionEngine", "SelfImprovementEngine",
]
