"""Run the complete lightweight workflow on the bundled example data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fault_etas_network.cascades import build_cascades, cascade_retention, event_adjacency
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.construction import aggregate_probabilities, build_directed_graph, symmetrize
from fault_etas_network.io import load_inputs, write_graph_json
from fault_etas_network.metrics import summarize_graph
from fault_etas_network.null_models import rewire_degree_preserving, rewire_spatially_constrained


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/example"))
    parser.add_argument("--output", type=Path, default=Path("results/example"))
    parser.add_argument("--resolution", type=float, default=0.5)
    args = parser.parse_args()

    arrays = load_inputs(args.input)
    cumulative, weights, counts = aggregate_probabilities(
        arrays["source"], arrays["target"], arrays["probability"],
        arrays["event_to_cell"], n_cells=len(arrays["positions"]),
        cumulative_threshold=0.001,
    )
    directed = build_directed_graph(
        weights, positions=arrays["positions"], event_counts=counts,
        edge_threshold=0.0,
    )
    graph = symmetrize(directed)
    labels, communities = detect_communities(graph, resolution=args.resolution)

    adjacency = event_adjacency(
        arrays["source"], arrays["target"], arrays["probability"], threshold=0.1
    )
    sources = np.flatnonzero(arrays["magnitude"] >= 5.0)
    retention = cascade_retention(
        build_cascades(adjacency, sources), arrays["event_to_cell"], labels
    )

    null_rw = rewire_degree_preserving(graph, swaps_per_edge=1, seed=42)
    null_sr = rewire_spatially_constrained(
        graph, n_distance_bins=1, swaps_per_edge=0.25, seed=42
    )
    summary = {
        "network": summarize_graph(graph),
        "community": {
            "resolution": args.resolution,
            "n_communities": len(communities),
            "modularity": modularity(graph, communities, resolution=args.resolution),
        },
        "cascade": retention,
        "null_smoke_test": {
            "observed_edges": graph.number_of_edges(),
            "rewired_edges": null_rw.number_of_edges(),
            "spatially_rewired_edges": null_sr.number_of_edges(),
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    write_graph_json(directed, args.output / "directed_network.json")
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
