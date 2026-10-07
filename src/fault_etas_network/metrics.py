"""Network summary metrics used in the manuscript."""

from __future__ import annotations

import networkx as nx
import numpy as np


def gini(values) -> float:
    """Return the Gini coefficient of nonnegative values."""
    values = np.asarray(list(values), dtype=float)
    if values.size == 0 or np.any(values < 0):
        raise ValueError("Gini input must be a nonempty nonnegative sequence")
    total = values.sum()
    if total == 0:
        return 0.0
    ordered = np.sort(values)
    ranks = np.arange(1, len(ordered) + 1)
    return float((2 * np.sum(ranks * ordered) / (len(ordered) * total)) - (len(ordered) + 1) / len(ordered))


def summarize_graph(graph: nx.Graph, *, weight: str = "weight") -> dict[str, float]:
    """Calculate compact structural summaries for a symmetrized graph."""
    degrees = np.fromiter((d for _, d in graph.degree()), dtype=float)
    strengths = np.fromiter((d for _, d in graph.degree(weight=weight)), dtype=float)
    return {
        "n_nodes": int(graph.number_of_nodes()),
        "n_edges": int(graph.number_of_edges()),
        "mean_degree": float(degrees.mean()) if len(degrees) else 0.0,
        "degree_gini": gini(degrees) if len(degrees) else 0.0,
        "strength_gini": gini(strengths) if len(strengths) else 0.0,
        "clustering_unweighted": float(nx.average_clustering(graph, weight=None)),
        "clustering_weighted": float(nx.average_clustering(graph, weight=weight)),
    }
