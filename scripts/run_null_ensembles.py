"""Run the two nested rewiring null ensembles used in the manuscript."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

from fault_etas_network.cascades import build_cascades, cascade_retention, event_adjacency
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.construction import aggregate_probabilities, build_directed_graph, symmetrize
from fault_etas_network.io import load_inputs
from fault_etas_network.holdout import chronological_masks
from fault_etas_network.metrics import summarize_graph
from fault_etas_network.null_models import rewire_degree_preserving, rewire_spatially_constrained


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--config", type=Path, default=Path("configs/paper.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--realizations", type=int, default=None)
    parser.add_argument("--temporal-holdout", action="store_true")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    arrays = load_inputs(args.input)
    net = config["network"]
    pair_mask = np.ones(len(arrays["source"]), dtype=bool)
    normalization_cells = arrays["event_to_cell"]
    source_mask = arrays["magnitude"] >= config["cascade"]["source_magnitude"]
    if args.temporal_holdout:
        cutoff, train, test, _ = chronological_masks(
            arrays["source"], arrays["target"], len(arrays["event_to_cell"]),
            config["temporal_holdout"]["training_fraction"],
        )
        pair_mask = train
        cascade_pair_mask = test
        normalization_cells = arrays["event_to_cell"][:cutoff]
        source_mask &= np.arange(len(source_mask)) >= cutoff
    else:
        cascade_pair_mask = pair_mask
    _, weights, counts = aggregate_probabilities(
        arrays["source"][pair_mask], arrays["target"][pair_mask],
        arrays["probability"][pair_mask], normalization_cells,
        n_cells=len(arrays["positions"]),
        cumulative_threshold=net["cumulative_triggering_threshold"],
    )
    observed = symmetrize(build_directed_graph(
        weights, positions=arrays["positions"], event_counts=counts,
        edge_threshold=net["cell_edge_threshold"],
    ))
    adjacency = event_adjacency(
        arrays["source"][cascade_pair_mask], arrays["target"][cascade_pair_mask],
        arrays["probability"][cascade_pair_mask],
        threshold=config["cascade"]["probability_threshold"],
    )
    sources = np.flatnonzero(source_mask)
    cascades = build_cascades(adjacency, sources)
    settings = config["null_models"]
    realizations = settings["realizations"] if args.realizations is None else args.realizations
    seed_sequence = np.random.SeedSequence(settings["seed"])
    child_seeds = iter(seed_sequence.spawn(2 * realizations))
    rows = []
    for realization in range(realizations):
        seeds = [int(next(child_seeds).generate_state(1)[0]) for _ in range(2)]
        nulls = {
            "N_RW": rewire_degree_preserving(
                observed, swaps_per_edge=settings["swaps_per_edge"], seed=seeds[0]
            ),
            "N_SR": rewire_spatially_constrained(
                observed, n_distance_bins=settings["distance_bins"],
                swaps_per_edge=settings["swaps_per_edge"], seed=seeds[1],
            ),
        }
        for name, graph in nulls.items():
            structural = summarize_graph(graph)
            for resolution in config["community"]["resolutions"]:
                labels, communities = detect_communities(
                    graph, resolution=resolution,
                    seed=config["community"]["seed"] + realization,
                )
                rows.append({
                    "null_model": name,
                    "realization": realization,
                    "resolution": resolution,
                    "clustering_unweighted": structural["clustering_unweighted"],
                    "clustering_weighted": structural["clustering_weighted"],
                    "n_communities": len(communities),
                    "modularity": modularity(graph, communities, resolution=resolution),
                    **cascade_retention(
                        cascades, arrays["event_to_cell"], labels,
                        min_source_community_size=config["cascade"]["minimum_source_community_nodes"],
                    ),
                })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
