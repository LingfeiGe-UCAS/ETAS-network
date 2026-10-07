"""Final accepted-swap null algorithms; unfinished randomizations raise an error."""
import networkx as nx
import numpy as np
from ._rewire_kernel import _global_distance_bin_rewire

EARTH_RADIUS_KM = 6371.0088

def distance_matrix(positions):
    lon, lat = np.radians(np.asarray(positions, dtype=float)[:, :2]).T
    result = np.empty((len(lon), len(lon)), dtype=np.float32)
    for start in range(0, len(lon), 256):
        stop = min(start + 256, len(lon))
        a = np.sin((lat[start:stop, None] - lat) / 2)**2
        a += np.cos(lat[start:stop, None]) * np.cos(lat) * np.sin((lon[start:stop, None] - lon) / 2)**2
        result[start:stop] = 2 * EARTH_RADIUS_KM * np.arcsin(np.minimum(1, np.sqrt(a)))
    return result

def _rewire(graph, swaps_per_edge, seed, weight, bins, spatial):
    if graph.is_directed() or graph.is_multigraph() or nx.number_of_selfloops(graph):
        raise ValueError('Rewiring requires a simple undirected graph without self-loops')
    if swaps_per_edge <= 0 or bins < 1:
        raise ValueError('Swap count and number of bins must be positive')
    nodes = sorted(graph)
    index = {n: i for i, n in enumerate(nodes)}
    edges = [(min(index[u], index[v]), max(index[u], index[v]), float(d.get(weight, 1)))
             for u, v, d in graph.edges(data=True)]
    if len(nodes) < 4 or len(edges) < 2:
        raise ValueError('Too few nodes or edges for double-edge swaps')
    u = np.array([e[0] for e in edges], dtype=np.int32)
    v = np.array([e[1] for e in edges], dtype=np.int32)
    w = np.array([e[2] for e in edges], dtype=float)
    pair_bins = np.zeros((len(nodes), len(nodes)), dtype=np.int16)
    if spatial and bins > 1:
        positions = np.array([graph.nodes[n]['position'] for n in nodes], dtype=float)
        if not np.all(np.isfinite(positions)):
            raise ValueError('Node positions must be finite longitude/latitude pairs')
        distances = distance_matrix(positions)
        cuts = np.unique(np.quantile(distances[u, v].astype(float), np.linspace(0, 1, bins + 1))[1:-1])
        pair_bins = np.searchsorted(cuts, distances, side='right').astype(np.int16)
    edge_bins = pair_bins[u, v]
    adjacency = np.zeros(pair_bins.shape, dtype=np.uint8)
    adjacency[u, v] = adjacency[v, u] = 1
    seed = int(np.random.SeedSequence().generate_state(1)[0]) if seed is None else int(seed)
    a, b, values, labels, accepted, attempts = _global_distance_bin_rewire(
        u, v, w, edge_bins, pair_bins, adjacency, float(swaps_per_edge), 1000, seed)
    target = max(1, int(np.ceil(swaps_per_edge * len(w))))
    if accepted != target:
        raise RuntimeError(f'Only {accepted}/{target} accepted swaps after {attempts} proposals; realization rejected')
    if not spatial:
        values = np.random.default_rng(seed).permutation(values)
    null = nx.Graph()
    null.add_nodes_from((n, dict(graph.nodes[n])) for n in nodes)
    for x, y, value in zip(a, b, values):
        null.add_edge(nodes[x], nodes[y], **{weight: float(value)})
    null.graph.update(accepted_swaps=int(accepted), attempted_swaps=int(attempts),
                      acceptance_rate=accepted / attempts, rewiring_seed=seed)
    return null

def rewire_degree_preserving(graph, *, swaps_per_edge=40., seed=None, weight='weight'):
    return _rewire(graph, swaps_per_edge, seed, weight, 1, False)

def rewire_spatially_constrained(graph, *, n_distance_bins=10, swaps_per_edge=640., seed=None, weight='weight'):
    # Weights travel with distance classes during swaps; no final reshuffle.
    return _rewire(graph, swaps_per_edge, seed, weight, n_distance_bins, True)
