"""Event-level cascade construction and community retention."""

from __future__ import annotations

from collections import defaultdict, deque
import numpy as np


def event_adjacency(source, target, probability, *, threshold: float = 0.1):
    """Build an adjacency list from event pairs exceeding a probability threshold."""
    adjacency: dict[int, list[int]] = defaultdict(list)
    for i, j, p in zip(source, target, probability):
        if p > threshold:
            adjacency[int(i)].append(int(j))
    return dict(adjacency)


def build_cascades(adjacency: dict[int, list[int]], sources) -> dict[int, set[int]]:
    """Return all events recursively reachable from each selected source."""
    cascades: dict[int, set[int]] = {}
    for root in sources:
        root = int(root)
        reached: set[int] = set()
        queue = deque(adjacency.get(root, []))
        while queue:
            event = queue.popleft()
            if event == root or event in reached:
                continue
            reached.add(event)
            queue.extend(adjacency.get(event, []))
        cascades[root] = reached
    return cascades


def cascade_retention(
    cascades: dict[int, set[int]],
    event_to_cell: np.ndarray,
    cell_to_community: dict[int, int],
    *,
    min_source_community_size: int = 1,
) -> dict[str, float | int]:
    """Fraction of cascade-associated events retained in the source community."""
    event_to_cell = np.asarray(event_to_cell, dtype=np.int64)
    sizes: dict[int, int] = defaultdict(int)
    for community in cell_to_community.values():
        sizes[int(community)] += 1
    retained = total = used_sources = skipped_sources = 0
    for root, reached in cascades.items():
        if root >= len(event_to_cell):
            skipped_sources += 1
            continue
        root_cell = int(event_to_cell[root])
        root_community = cell_to_community.get(root_cell)
        if root_community is None or sizes[root_community] < min_source_community_size:
            skipped_sources += 1
            continue
        used_sources += 1
        for event in reached:
            if event == root:
                continue
            if event >= len(event_to_cell):
                continue
            community = cell_to_community.get(int(event_to_cell[event]))
            if community is None:
                continue
            total += 1
            retained += int(community == root_community)
    return {
        "retention": float(retained / total) if total else float("nan"),
        "retained_events": retained,
        "cascade_events": total,
        "used_sources": used_sources,
        "skipped_sources": skipped_sources,
    }
