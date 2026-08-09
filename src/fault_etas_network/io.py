"""Small, explicit file formats for reproducible analysis."""

from __future__ import annotations

from pathlib import Path
import json
import networkx as nx
import numpy as np
import pandas as pd


def load_inputs(directory: str | Path) -> dict[str, np.ndarray]:
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
    return {
        "event_to_cell": events.cell_id.to_numpy(dtype=np.int64),
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
