"""Small, explicit file formats for reproducible analysis."""

from __future__ import annotations

from pathlib import Path
import json
import networkx as nx
import numpy as np
import pandas as pd


def load_inputs(directory: str | Path, *, maximum_fault_distance_km=None,
                prefiltered=False) -> dict[str, np.ndarray]:
    """Load events.csv, event_pairs.csv, and cells.csv from a data directory."""
    directory = Path(directory)
    events = pd.read_csv(directory / "events.csv")
    pairs = pd.read_csv(directory / "event_pairs.csv")
    cells = pd.read_csv(directory / "cells.csv")
    required_events = {"event_id", "cell_id", "magnitude", "time"}
    required_pairs = {"source", "target", "probability"}
    required_cells = {"cell_id", "longitude", "latitude"}
    for required, columns, name in (
        (required_events, set(events), "events.csv"),
        (required_pairs, set(pairs), "event_pairs.csv"),
        (required_cells, set(cells), "cells.csv"),
    ):
        missing = required - columns
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")
    if not np.array_equal(events.event_id.to_numpy(), np.arange(len(events))):
        raise ValueError("event_id must be contiguous and zero based")
    cells = cells.sort_values("cell_id")
    if not np.array_equal(cells.cell_id.to_numpy(), np.arange(len(cells))):
        raise ValueError("cell_id must be contiguous and zero based")
    times = events.time.to_numpy(float)
    if not np.isfinite(times).all() or np.any(np.diff(times) < 0):
        raise ValueError("events must have finite chronological numeric times")
    mapping = events.cell_id.to_numpy(dtype=int)
    if np.any(mapping < -1) or np.any(mapping >= len(cells)):
        raise ValueError("event cell_id must be -1 or an existing cell")
    if maximum_fault_distance_km is not None:
        limit = float(maximum_fault_distance_km)
        if not np.isfinite(limit) or limit < 0:
            raise ValueError('maximum_fault_distance_km must be finite and nonnegative')
        if 'fault_distance_km' in events:
            distances = events.fault_distance_km.to_numpy(float)
            if not np.isfinite(distances).all() or np.any(distances < 0):
                raise ValueError('fault_distance_km must contain finite nonnegative distances')
            mapping = mapping.copy()
            mapping[distances > limit] = -1
        elif not prefiltered:
            raise ValueError('Provide fault_distance_km or explicitly confirm upstream screening with --prefiltered')
    source, target = pairs.source.to_numpy(dtype=int), pairs.target.to_numpy(dtype=int)
    if np.any(source < 0) or np.any(target < 0) or np.any(source >= len(events)) or np.any(target >= len(events)):
        raise ValueError("pair IDs must reference existing events")
    if np.any(times[source] >= times[target]):
        raise ValueError("triggering pairs must point strictly forward in time")
    probabilities = pairs.probability.to_numpy(float)
    if not np.isfinite(probabilities).all() or np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must be finite and in [0, 1]")
    return {
        "event_to_cell": mapping.astype(np.int64),
        "magnitude": events.magnitude.to_numpy(float),
        "time": events.time.to_numpy(float),
        "source": pairs.source.to_numpy(dtype=np.int64),
        "target": pairs.target.to_numpy(dtype=np.int64),
        "probability": pairs.probability.to_numpy(float),
        "positions": cells[["longitude", "latitude"]].to_numpy(float),
    }


def write_graph_json(graph: nx.Graph, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        # The default key is ``links`` in NetworkX 3.2 and ``edges`` in newer
        # releases. Using the default keeps this lightweight exporter compatible
        # across the supported NetworkX 3.x series.
        json.dump(nx.node_link_data(graph), stream, indent=2)
