"""Degree-preserving rewiring null models."""

from __future__ import annotations

import math
import networkx as nx
import numpy as np


EARTH_RADIUS_KM = 6371.0088


def _great_circle_km(first, second) -> float:
    lon1, lat1 = map(math.radians, first[:2])
    lon2, lat2 = map(math.radians, second[:2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(value)))


def _distance_bins(graph: nx.Graph, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    edges = list(graph.edges())
    positions = nx.get_node_attributes(graph, "position")
    if len(positions) != graph.number_of_nodes():
        raise ValueError("spatial rewiring requires a position attribute on every node")
    distances = np.asarray([_great_circle_km(positions[u], positions[v]) for u, v in edges])
    if n_bins <= 1:
        return np.zeros(len(edges), dtype=int), np.asarray([-np.inf, np.inf])
    quantiles = np.quantile(distances, np.linspace(0, 1, n_bins + 1))
    boundaries = np.unique(quantiles)
    labels = np.searchsorted(boundaries[1:-1], distances, side="right")
    return labels.astype(int), boundaries


def rewire_degree_preserving(
    graph: nx.Graph,
    *,
    swaps_per_edge: float = 10.0,
    seed: int | None = None,
    weight: str = "weight",
) -> nx.Graph:
    """N_RW: preserve nodes, degrees, and the global weight distribution."""
    rng = np.random.default_rng(seed)
    null = nx.Graph()
    null.add_nodes_from(graph.nodes(data=True))
    null.add_edges_from(graph.edges())
    target = max(1, int(round(swaps_per_edge * graph.number_of_edges())))
    nx.double_edge_swap(null, nswap=target, max_tries=max(100, 50 * target), seed=seed)
    weights = np.asarray([data.get(weight, 1.0) for _, _, data in graph.edges(data=True)], dtype=float)
    rng.shuffle(weights)
    for (u, v), value in zip(null.edges(), weights):
        null[u][v][weight] = float(value)
    return null


def rewire_spatially_constrained(
    graph: nx.Graph,
    *,
    n_distance_bins: int = 10,
    swaps_per_edge: float = 10.0,
    seed: int | None = None,
    weight: str = "weight",
) -> nx.Graph:
    """N_SR: preserve degrees and equal-frequency edge-distance classes.

    A swap (a,b),(c,d) -> (a,d),(c,b) is accepted only when the unordered
    pair of original distance-bin labels equals that of the proposed edges.
    Weights are shuffled only among edges in the same resulting distance bin.
    """
    rng = np.random.default_rng(seed)
    null = graph.copy()
    edges = [tuple(edge) for edge in null.edges()]
    _, boundaries = _distance_bins(graph, n_distance_bins)
    positions = nx.get_node_attributes(graph, "position")

    def label(u, v):
        distance = _great_circle_km(positions[u], positions[v])
        return int(np.searchsorted(boundaries[1:-1], distance, side="right"))

    target = max(1, int(round(swaps_per_edge * len(edges))))
    accepted = attempts = 0
    max_attempts = max(1000, target * 200)
    while accepted < target and attempts < max_attempts:
        attempts += 1
        i, j = rng.choice(len(edges), size=2, replace=False)
        a, b = edges[i]
        c, d = edges[j]
        if len({a, b, c, d}) < 4:
            continue
        if rng.random() < 0.5:
            c, d = d, c
        if a == d or c == b or null.has_edge(a, d) or null.has_edge(c, b):
            continue
        if sorted((label(a, b), label(c, d))) != sorted((label(a, d), label(c, b))):
            continue
        null.remove_edge(a, b)
        null.remove_edge(c, d)
        null.add_edge(a, d)
        null.add_edge(c, b)
        edges[i] = (a, d)
        edges[j] = (c, b)
        accepted += 1

    original_by_bin: dict[int, list[float]] = {}
    for u, v, data in graph.edges(data=True):
        original_by_bin.setdefault(label(u, v), []).append(float(data.get(weight, 1.0)))
    new_by_bin: dict[int, list[tuple[int, int]]] = {}
    for u, v in null.edges():
        new_by_bin.setdefault(label(u, v), []).append((u, v))
    for bin_id, bin_edges in new_by_bin.items():
        values = np.asarray(original_by_bin[bin_id], dtype=float)
        if len(values) != len(bin_edges):
            raise RuntimeError("distance-bin edge counts changed during rewiring")
        rng.shuffle(values)
        for (u, v), value in zip(bin_edges, values):
            null[u][v][weight] = float(value)
    null.graph["accepted_swaps"] = accepted
    null.graph["attempted_swaps"] = attempts
    return null
