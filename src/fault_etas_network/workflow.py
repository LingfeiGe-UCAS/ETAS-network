"""Shared observed/null workflow for prepared probability and cell-assignment inputs."""
import argparse
import json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import yaml
from .io import load_inputs, write_graph_json
from .construction import aggregate_probabilities, build_directed_graph, symmetrize
from .communities import detect_communities, modularity
from .cascades import event_adjacency, build_cascades
from .holdout import chronological_masks
from .samples import freeze_sample, evaluate_sample, load_sample
from .metrics import summarize_graph
from .null_models import rewire_degree_preserving, rewire_spatially_constrained


def run(directory, config, output, holdout=False, realizations=0, frozen_path=None, prefiltered=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    arrays = load_inputs(directory,
                         maximum_fault_distance_km=config['network'].get('maximum_fault_distance_km'),
                         prefiltered=prefiltered)
    mapping = arrays['event_to_cell']
    n = len(mapping)
    train = test = np.ones(len(arrays['source']), dtype=bool)
    cutoff = 0
    norm = mapping
    cross = np.zeros(len(train), dtype=bool)
    if holdout:
        cutoff, train, test, cross = chronological_masks(arrays['source'], arrays['target'], n,
                                                        config['temporal_holdout']['training_fraction'])
        norm = mapping[:cutoff]
    _, weights, counts = aggregate_probabilities(
        arrays['source'][train], arrays['target'][train], arrays['probability'][train], norm,
        n_cells=len(arrays['positions']),
        cumulative_threshold=config['network']['cumulative_triggering_threshold'])
    directed = build_directed_graph(weights, positions=arrays['positions'], event_counts=counts)
    graph = symmetrize(directed)
    adjacency = event_adjacency(arrays['source'][test], arrays['target'][test], arrays['probability'][test],
                               threshold=config['cascade']['probability_threshold'])
    sources = np.flatnonzero((np.arange(n) >= cutoff) &
                            (arrays['magnitude'] >= config['cascade']['source_magnitude']))
    cascades = build_cascades(adjacency, sources)
    seeds = config['community']['seeds']
    resolutions = config['community']['resolutions']
    samples, observed, sample_frames, component_rows = {}, [], [], []
    structure = summarize_graph(graph)
    for eta in resolutions:
        labels, communities = detect_communities(graph, resolution=eta, seeds=seeds)
        if frozen_path:
            sample = load_sample(frozen_path, eta, mapping, labels)
        else:
            # Match the manuscript audit: seed 12345 selects eligibility;
            # best-of-20 labels subsequently evaluate exactly that frozen sample.
            eligibility, _ = detect_communities(graph, resolution=eta,
                                                seed=config['cascade']['eligibility_seed'])
            sample = freeze_sample(cascades, mapping, eligibility,
                                   config['cascade']['minimum_source_community_nodes'])
        samples[eta] = sample
        sample_frames.append(sample.assign(eta=eta))
        observed.append(dict(resolution=eta, n_communities=len(communities),
                             modularity=modularity(graph, communities, resolution=eta),
                             **structure, **evaluate_sample(sample, labels)))
        for number, component in enumerate(sorted(nx.connected_components(graph), key=len, reverse=True)):
            component_rows.append(dict(resolution=eta, component=number, nodes=len(component),
                                       node_fraction=len(component)/len(graph),
                                       communities=len({labels[u] for u in component})))
    pd.DataFrame(observed).to_csv(output/'observed.csv', index=False)
    pd.concat(sample_frames, ignore_index=True).to_csv(output/'fixed_memberships.csv', index=False)
    pd.DataFrame(component_rows).to_csv(output/'components.csv', index=False)
    write_graph_json(directed, output/'directed_network.json')
    pd.DataFrame([dict(test_events=n-cutoff,
                       represented_test_events=int(np.isin(mapping[cutoff:], list(graph)).sum()),
                       excluded_cross_boundary_pairs=int(cross.sum()),
                       training_nodes=len(graph), training_edges=graph.number_of_edges(),
                       magnitude_eligible_sources=len(sources),
                       downstream_memberships_before_coverage=sum(map(len, cascades.values())),
                       downstream_memberships_after_coverage=sum(
                           sum(int(mapping[e]) in graph for e in members)
                           for r, members in cascades.items() if int(mapping[r]) in graph))
                  ]).to_csv(output/'coverage.csv', index=False)
    rows = []
    settings = config['null_models']
    for i in range(realizations):
        for model in ['M_RW', 'M_SR']:
            seed = settings['seed'] + i + (100000 if model == 'M_SR' else 0)
            if model == 'M_RW':
                null = rewire_degree_preserving(graph, swaps_per_edge=settings['rw_swaps_per_edge'], seed=seed)
            else:
                null = rewire_spatially_constrained(graph, swaps_per_edge=settings['sr_swaps_per_edge'],
                                                    n_distance_bins=settings['distance_bins'], seed=seed)
            stats = summarize_graph(null)
            for eta in resolutions:
                labels, communities = detect_communities(null, resolution=eta, seeds=seeds)
                rows.append(dict(null_model=model, realization=i, resolution=eta,
                                 modularity=modularity(null, communities, resolution=eta),
                                 n_communities=len(communities), **stats, **null.graph,
                                 **evaluate_sample(samples[eta], labels)))
        pd.DataFrame(rows).to_csv(output/'null_realizations.csv', index=False)
    if rows:
        summary = []
        frame = pd.DataFrame(rows)
        obs = pd.DataFrame(observed).set_index('resolution')
        for (model, eta), part in frame.groupby(['null_model', 'resolution']):
            for metric in ['modularity', 'retention', 'clustering_unweighted', 'clustering_weighted']:
                values = part[metric].to_numpy()
                value = obs.loc[eta, metric]
                valid = np.isfinite(value) and np.isfinite(values).all()
                summary.append(dict(null_model=model, resolution=eta, metric=metric, observed=value,
                                    mean=float(values.mean()), p025=float(np.quantile(values, .025)),
                                    p975=float(np.quantile(values, .975)),
                                    p_ge=(1+int((values >= value).sum()))/(len(values)+1) if valid else np.nan,
                                    p_le=(1+int((values <= value).sum()))/(len(values)+1) if valid else np.nan))
        pd.DataFrame(summary).to_csv(output/'null_summary.csv', index=False)
    (output/'settings.json').write_text(json.dumps(dict(config=config, realizations=realizations,
        temporal_holdout=holdout, frozen_memberships_supplied=frozen_path is not None,
        upstream_screening_confirmed=prefiltered, networkx=nx.__version__), indent=2), encoding='utf-8')


def main(mode='observed'):
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--config', type=Path, default=Path('configs/paper.yaml'))
    parser.add_argument('--output', type=Path, required=True, help='Output directory')
    parser.add_argument('--realizations', type=int)
    parser.add_argument('--temporal-holdout', action='store_true')
    parser.add_argument('--fixed-memberships', type=Path)
    parser.add_argument('--prefiltered', action='store_true',
                        help='Confirm cell mapping already excludes events beyond the configured fault distance')
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding='utf-8'))
    number = (config['null_models']['realizations'] if args.realizations is None else args.realizations) if mode == 'null' else 0
    run(args.input, config, args.output, mode == 'holdout' or args.temporal_holdout,
        number, args.fixed_memberships, args.prefiltered)
