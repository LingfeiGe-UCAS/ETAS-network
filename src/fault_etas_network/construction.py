"""Construction of directed weighted networks from event-pair probabilities."""

from __future__ import annotations

import networkx as nx
import numpy as np
from scipy import sparse


def aggregate_probabilities(
    source: np.ndarray,
    target: np.ndarray,
    probability: np.ndarray,
    event_to_cell: np.ndarray,
    *,
    n_cells: int | None = None,
    pair_probability_threshold: float = 0.0,
    cumulative_threshold: float = 0.0,
) -> tuple[sparse.csr_matrix, sparse.csr_matrix, np.ndarray]:
    """Return cumulative and source-normalized cell matrices.

    The cumulative matrix is S = M.T @ P @ M.  The directed network weight
    W_uv is S_uv divided by the number of catalog events assigned to source
    cell u. Events assigned -1 are excluded.
    """
    source = np.asarray(source, dtype=np.int64)
    target = np.asarray(target, dtype=np.int64)
    probability = np.asarray(probability, dtype=float)
    event_to_cell = np.asarray(event_to_cell, dtype=np.int64)
    if not (source.shape == target.shape == probability.shape):
        raise ValueError("source, target, and probability must have equal shape")
    if np.any(source < 0) or np.any(target < 0):
        raise ValueError("event indexes must be nonnegative")
    if source.size and max(source.max(), target.max()) >= len(event_to_cell):
        raise ValueError("event-pair index exceeds event_to_cell length")
    if np.any((probability < 0) | (probability > 1)):
        raise ValueError("probabilities must lie in [0, 1]")

    valid_cells = event_to_cell[event_to_cell >= 0]
    inferred = int(valid_cells.max()) + 1 if valid_cells.size else 0
    n_cells = inferred if n_cells is None else int(n_cells)
    if inferred > n_cells:
        raise ValueError("n_cells is smaller than an assigned cell index")

    keep = (
        (probability > pair_probability_threshold)
        & (event_to_cell[source] >= 0)
        & (event_to_cell[target] >= 0)
    )
    rows = event_to_cell[source[keep]]
    cols = event_to_cell[target[keep]]
    cumulative = sparse.coo_matrix(
        (probability[keep], (rows, cols)), shape=(n_cells, n_cells)
    ).tocsr()
    cumulative.sum_duplicates()

    retained = cumulative.copy()
    retained.data[retained.data < cumulative_threshold] = 0.0
    retained.eliminate_zeros()

    counts = np.bincount(valid_cells, minlength=n_cells).astype(np.int64)
    inv_counts = np.zeros(n_cells, dtype=float)
    np.divide(1.0, counts, out=inv_counts, where=counts > 0)
    weights = sparse.diags(inv_counts) @ retained
    weights = weights.tocsr()
    weights.eliminate_zeros()
    return cumulative, weights, counts


def build_directed_graph(
    weights: sparse.spmatrix | np.ndarray,
    *,
    positions: np.ndarray | None = None,
    event_counts: np.ndarray | None = None,
    edge_threshold: float = 0.0,
    remove_self_loops: bool = False,
) -> nx.DiGraph:
    """Create a NetworkX directed graph from a cell-weight matrix."""
    matrix = sparse.coo_matrix(weights)
    graph = nx.DiGraph()
    graph.add_nodes_from(range(matrix.shape[0]))
    if positions is not None:
        positions = np.asarray(positions, dtype=float)
        if len(positions) != matrix.shape[0]:
            raise ValueError("positions must have one row per cell")
        nx.set_node_attributes(
            graph, {i: tuple(positions[i]) for i in range(len(positions))}, "position"
        )
    if event_counts is not None:
        nx.set_node_attributes(
            graph, {i: int(event_counts[i]) for i in range(len(event_counts))}, "event_count"
        )
    for u, v, value in zip(matrix.row, matrix.col, matrix.data):
        if value <= edge_threshold or (remove_self_loops and u == v):
            continue
        graph.add_edge(int(u), int(v), weight=float(value))
    isolates = [node for node, degree in graph.degree() if degree == 0]
    graph.remove_nodes_from(isolates)
    return graph


def symmetrize(graph: nx.DiGraph, *, weight: str = "weight") -> nx.Graph:
    """Return the weighted projection A_s = W + W.T with zero diagonal."""
    projected = nx.Graph()
    projected.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        if u == v:
            continue
        value = float(data.get(weight, 1.0))
        if projected.has_edge(u, v):
            projected[u][v][weight] += value
        else:
            projected.add_edge(u, v, **{weight: value})
    return projected
