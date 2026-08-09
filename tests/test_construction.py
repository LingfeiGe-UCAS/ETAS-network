import numpy as np

from fault_etas_network.construction import aggregate_probabilities, build_directed_graph, symmetrize


def test_matrix_aggregation_and_source_normalization():
    source = np.array([0, 1, 2])
    target = np.array([2, 2, 3])
    probability = np.array([0.4, 0.6, 0.5])
    event_to_cell = np.array([0, 0, 1, 1])
    cumulative, weights, counts = aggregate_probabilities(
        source, target, probability, event_to_cell
    )
    assert counts.tolist() == [2, 2]
    assert cumulative[0, 1] == 1.0
    assert weights[0, 1] == 0.5


def test_symmetrization_adds_reciprocal_weights():
    matrix = np.array([[0.0, 0.2], [0.3, 0.0]])
    directed = build_directed_graph(matrix)
    graph = symmetrize(directed)
    assert graph[0][1]["weight"] == 0.5
