"""Analysis entry point for licensed/prepared regional inputs.

Input directories must use the CSV schema documented in docs/data_format.md.
This script deliberately does not download or redistribute third-party data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml
import numpy as np

from fault_etas_network.cascades import build_cascades, cascade_retention, event_adjacency
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.construction import aggregate_probabilities, build_directed_graph, symmetrize
from fault_etas_network.io import load_inputs, write_graph_json
from fault_etas_network.metrics import summarize_graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/paper.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    arrays = load_inputs(args.input)
    net = config["network"]
    _, weights, counts = aggregate_probabilities(
        arrays["source"], arrays["target"], arrays["probability"],
        arrays["event_to_cell"], n_cells=len(arrays["positions"]),
        cumulative_threshold=net["cumulative_triggering_threshold"],
    )
    directed = build_directed_graph(
        weights, positions=arrays["positions"], event_counts=counts,
        edge_threshold=net["cell_edge_threshold"],
    )
    graph = symmetrize(directed)
    adjacency = event_adjacency(
        arrays["source"], arrays["target"], arrays["probability"],
        threshold=config["cascade"]["probability_threshold"],
    )
    source_events = np.flatnonzero(
        arrays["magnitude"] >= config["cascade"]["source_magnitude"]
    )
    cascades = build_cascades(adjacency, source_events)
    rows = []
    for resolution in config["community"]["resolutions"]:
        labels, communities = detect_communities(
            graph, resolution=resolution, seed=config["community"]["seed"]
        )
        rows.append({
            "resolution": resolution,
            "n_communities": len(communities),
            "modularity": modularity(graph, communities, resolution=resolution),
            **cascade_retention(
                cascades, arrays["event_to_cell"], labels,
                min_source_community_size=config["cascade"]["minimum_source_community_nodes"],
            ),
        })
    args.output.mkdir(parents=True, exist_ok=True)
    write_graph_json(directed, args.output / "directed_network.json")
    (args.output / "network_summary.json").write_text(
        json.dumps(summarize_graph(graph), indent=2, allow_nan=True), encoding="utf-8"
    )
    (args.output / "community_retention.json").write_text(
        json.dumps(rows, indent=2, allow_nan=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
