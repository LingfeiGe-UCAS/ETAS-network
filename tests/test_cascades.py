import numpy as np

from fault_etas_network.cascades import build_cascades, cascade_retention


def test_recursive_reachability_and_retention():
    cascades = build_cascades({0: [1], 1: [2], 2: [3]}, [0])
    assert cascades[0] == {1, 2, 3}
    result = cascade_retention(
        cascades,
        np.array([0, 0, 1, 2]),
        {0: 4, 1: 4, 2: 5},
    )
    assert result["cascade_events"] == 3
    assert result["retained_events"] == 2
    assert np.isclose(result["retention"], 2 / 3)
