"""Detect communities in the earlier catalog and evaluate later cascades."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import yaml

from fault_etas_network.cascades import build_cascades, cascade_retention, event_adjacency
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.construction import aggregate_probabilities, build_directed_graph, symmetrize
from fault_etas_network.holdout import chronological_masks
from fault_etas_network.io import load_inputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/paper.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    arrays = load_inputs(args.input)
    cutoff, train, test, cross = chronological_masks(
        arrays["source"], arrays["target"], len(arrays["event_to_cell"]),
        config["temporal_holdout"]["training_fraction"],
    )
    _, weights, counts = aggregate_probabilities(
        arrays["source"][train], arrays["target"][train], arrays["probability"][train],
        arrays["event_to_cell"][:cutoff], n_cells=len(arrays["positions"]),
        cumulative_threshold=config["network"]["cumulative_triggering_threshold"],
    )
    directed = build_directed_graph(
        weights, positions=arrays["positions"], event_counts=counts,
        edge_threshold=config["network"]["cell_edge_threshold"],
    )
    graph = symmetrize(directed)
    adjacency = event_adjacency(
        arrays["source"][test], arrays["target"][test], arrays["probability"][test],
        threshold=config["cascade"]["probability_threshold"],
    )
    sources = np.flatnonzero(
        (np.arange(len(arrays["magnitude"])) >= cutoff)
        & (arrays["magnitude"] >= config["cascade"]["source_magnitude"])
    )
    cascades = build_cascades(adjacency, sources)
    results = []
    for resolution in config["community"]["resolutions"]:
        labels, communities = detect_communities(
            graph, resolution=resolution, seed=config["community"]["seed"]
        )
        results.append({
            "resolution": resolution,
            "n_communities": len(communities),
            "modularity": modularity(graph, communities, resolution=resolution),
            **cascade_retention(
                cascades, arrays["event_to_cell"], labels,
                min_source_community_size=config["cascade"]["minimum_source_community_nodes"],
            ),
        })
    output = {
        "cutoff_event": cutoff,
        "training_pairs": int(train.sum()),
        "test_pairs": int(test.sum()),
        "excluded_cross_boundary_pairs": int(cross.sum()),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=True), encoding="utf-8")


if __name__ == "__main__":
    main()
