"""Accepted-swap kernel copied from the final experiment (optional Numba)."""
import numpy as np
try:
    from numba import njit
except ImportError:
    def njit(**kwargs):
        return lambda function: function

@njit(cache=True)
def _global_distance_bin_rewire(
    edge_u_initial: np.ndarray,
    edge_v_initial: np.ndarray,
    weight_initial: np.ndarray,
    edge_bins_initial: np.ndarray,
    pair_bins: np.ndarray,
    adjacency_initial: np.ndarray,
    swap_factor: float,
    max_tries_factor: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]:
    np.random.seed(seed)
    edge_u = edge_u_initial.copy()
    edge_v = edge_v_initial.copy()
    weights = weight_initial.copy()
    edge_bins = edge_bins_initial.copy()
    adjacency = adjacency_initial.copy()
    n_edges = len(edge_u)
    target_swaps = max(1, int(np.ceil(swap_factor * n_edges)))
    max_attempts = max(1000, max_tries_factor * target_swaps)
    accepted = 0
    attempts = 0

    while accepted < target_swaps and attempts < max_attempts:
        attempts += 1
        edge_1 = np.random.randint(0, n_edges)
        edge_2 = np.random.randint(0, n_edges)
        if edge_1 == edge_2:
            continue

        a = edge_u[edge_1]
        b = edge_v[edge_1]
        c = edge_u[edge_2]
        d = edge_v[edge_2]
        if a == c or a == d or b == c or b == d:
            continue

        if np.random.random() < 0.5:
            p = a
            q = d
            r = c
            s = b
        else:
            p = a
            q = c
            r = b
            s = d

        if p > q:
            p, q = q, p
        if r > s:
            r, s = s, r
        if p == q or r == s or (p == r and q == s):
            continue
        if adjacency[p, q] or adjacency[r, s]:
            continue

        old_bin_1 = edge_bins[edge_1]
        old_bin_2 = edge_bins[edge_2]
        new_bin_1 = pair_bins[p, q]
        new_bin_2 = pair_bins[r, s]
        same_order = (
            new_bin_1 == old_bin_1 and new_bin_2 == old_bin_2
        )
        swapped_order = (
            new_bin_1 == old_bin_2 and new_bin_2 == old_bin_1
        )
        if not same_order and not swapped_order:
            continue

        adjacency[a, b] = 0
        adjacency[b, a] = 0
        adjacency[c, d] = 0
        adjacency[d, c] = 0
        adjacency[p, q] = 1
        adjacency[q, p] = 1
        adjacency[r, s] = 1
        adjacency[s, r] = 1

        edge_u[edge_1] = p
        edge_v[edge_1] = q
        edge_u[edge_2] = r
        edge_v[edge_2] = s
        if swapped_order and old_bin_1 != old_bin_2:
            temporary_weight = weights[edge_1]
            weights[edge_1] = weights[edge_2]
            weights[edge_2] = temporary_weight
        edge_bins[edge_1] = new_bin_1
        edge_bins[edge_2] = new_bin_2
        accepted += 1

    return edge_u, edge_v, weights, edge_bins, accepted, attempts

