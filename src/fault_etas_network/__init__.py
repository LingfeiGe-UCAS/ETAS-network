"""Fault-associated ETAS network analysis."""

from .construction import aggregate_probabilities, build_directed_graph, symmetrize
from .communities import detect_communities, modularity
from .cascades import build_cascades, cascade_retention

__version__ = "1.1.0"

__all__ = [
    "aggregate_probabilities",
    "build_directed_graph",
    "symmetrize",
    "detect_communities",
    "modularity",
    "build_cascades",
    "cascade_retention",
]
