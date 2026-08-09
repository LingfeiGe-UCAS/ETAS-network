import numpy as np

from fault_etas_network.holdout import chronological_masks


def test_chronological_masks_exclude_cross_boundary_pairs():
    source = np.array([0, 1, 4, 5, 2])
    target = np.array([1, 4, 5, 6, 6])
    cutoff, train, test, cross = chronological_masks(source, target, 10, 0.5)
    assert cutoff == 5
    assert train.tolist() == [True, True, False, False, False]
    assert test.tolist() == [False, False, False, True, False]
    assert cross.tolist() == [False, False, True, False, True]
