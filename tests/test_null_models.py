import networkx as nx
import numpy as np

from fault_etas_network.null_models import rewire_degree_preserving


def test_rewired_null_preserves_degrees_and_weights():
    graph = nx.cycle_graph(8)
    for index, (u, v) in enumerate(graph.edges()):
        graph[u][v]["weight"] = float(index + 1)
    null = rewire_degree_preserving(graph, swaps_per_edge=1, seed=7)
    assert sorted(dict(graph.degree()).values()) == sorted(dict(null.degree()).values())
    original = sorted(data["weight"] for _, _, data in graph.edges(data=True))
    rewired = sorted(data["weight"] for _, _, data in null.edges(data=True))
    assert np.allclose(original, rewired)
