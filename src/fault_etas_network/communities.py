"""Weighted community detection and modularity."""

from __future__ import annotations

import networkx as nx


def detect_communities(
    graph: nx.Graph,
    *,
    resolution: float = 1.0,
    weight: str = "weight",
    seed: int = 42,
    seeds=None,
) -> tuple[dict[int, int], list[set[int]]]:
    """Detect Louvain communities and return node labels and node sets."""
    seeds = [seed] if seeds is None else list(seeds)
    if not seeds:
        raise ValueError("At least one Louvain seed is required")
    if graph.number_of_edges() == 0:
        communities = [{node} for node in graph]
    else:
        best_q = float('-inf')
        for restart_seed in seeds:
            candidate = list(nx.community.louvain_communities(
                graph, weight=weight, resolution=resolution, seed=restart_seed))
            q = modularity(graph, candidate, resolution=resolution, weight=weight)
            if q > best_q:
                best_q, communities = q, candidate
    communities.sort(key=lambda members: (-len(members), min(members)))
    labels = {
        int(node): community_id
        for community_id, members in enumerate(communities)
        for node in members
    }
    return labels, communities


def modularity(
    graph: nx.Graph,
    communities: list[set[int]],
    *,
    resolution: float = 1.0,
    weight: str = "weight",
) -> float:
    """Calculate generalized weighted modularity for an undirected graph."""
    if graph.number_of_edges() == 0:
        return float('nan')
    return float(
        nx.community.modularity(
            graph, communities, weight=weight, resolution=resolution
        )
    )
