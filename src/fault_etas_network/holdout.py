"""Chronological separation of network construction and cascade evaluation."""

from __future__ import annotations

import numpy as np


def chronological_masks(source, target, n_events: int, training_fraction: float = 0.7):
    """Return training, test, and cross-boundary event-pair masks."""
    if not 0 < training_fraction < 1:
        raise ValueError("training_fraction must lie strictly between zero and one")
    cutoff = int(np.floor(training_fraction * n_events))
    source = np.asarray(source)
    target = np.asarray(target)
    training = (source < cutoff) & (target < cutoff)
    test = (source >= cutoff) & (target >= cutoff)
    cross = ~(training | test)
    return cutoff, training, test, cross
