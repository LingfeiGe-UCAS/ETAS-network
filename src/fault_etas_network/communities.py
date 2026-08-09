"""Weighted community detection and modularity."""

from __future__ import annotations

import networkx as nx


def detect_communities(
    graph: nx.Graph,
    *,
    resolution: float = 1.0,
    weight: str = "weight",
    seed: int = 42,
) -> tuple[dict[int, int], list[set[int]]]:
    """Detect Louvain communities and return node labels and node sets."""
    communities = list(
        nx.community.louvain_communities(
            graph, weight=weight, resolution=resolution, seed=seed
        )
    )
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
    return float(
        nx.community.modularity(
            graph, communities, weight=weight, resolution=resolution
        )
    )
