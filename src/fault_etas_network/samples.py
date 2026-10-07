"""Freeze source/member pairs before comparing observed and randomized labels."""
from collections import Counter
import numpy as np
import pandas as pd


def freeze_sample(cascades, event_to_cell, labels, minimum_nodes=5):
    sizes = Counter(labels.values())
    records = []
    for source, members in cascades.items():
        node = int(event_to_cell[source])
        if node not in labels or sizes[labels[node]] < minimum_nodes:
            continue
        for event in sorted(members):
            target = int(event_to_cell[event])
            if event != source and target in labels:
                records.append((source, node, event, target))
    return pd.DataFrame(records, columns=['source_event', 'source_node', 'event', 'event_node'])


def evaluate_sample(sample, labels):
    """No source reselection; missing labels are an error, not a silent exclusion."""
    same = np.array([labels[int(u)] == labels[int(v)]
                     for u, v in zip(sample.source_node, sample.event_node)], dtype=bool)
    return dict(retention=float(same.mean()) if len(same) else float('nan'),
                retained_memberships=int(same.sum()), downstream_memberships=len(same),
                source_events=int(sample.source_event.nunique()))


def load_sample(path, resolution, event_to_cell, labels):
    """Read frozen manuscript memberships; remove source rows before evaluation."""
    frame = pd.read_csv(path)
    frame = frame.loc[np.isclose(frame.eta, resolution) & (frame.source_event != frame.event)].copy()
    for event_col, node_col in [('source_event', 'source_node'), ('event', 'event_node')]:
        ids = frame[event_col].to_numpy(dtype=int)
        if np.any(ids < 0) or np.any(ids >= len(event_to_cell)):
            raise ValueError('Frozen membership event IDs do not match the input catalog')
        if not np.array_equal(event_to_cell[ids], frame[node_col].to_numpy(dtype=int)):
            raise ValueError('Frozen membership node IDs do not match the supplied mapping')
        if not set(frame[node_col]).issubset(labels):
            raise ValueError('Frozen memberships contain nodes missing from the training network')
    if frame.duplicated(['source_event', 'event']).any():
        raise ValueError('Duplicate source/event memberships')
    return frame
