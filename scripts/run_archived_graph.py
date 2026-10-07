"""Recompute best-of-20 Q and fixed-sample retention on the bundled derived graphs."""
import argparse
import json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import yaml
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.samples import evaluate_sample
from fault_etas_network.metrics import summarize_graph
from fault_etas_network.null_models import rewire_degree_preserving, rewire_spatially_constrained


def load_graph(path):
    g = nx.Graph()
    for row in pd.read_csv(path/'nodes.csv').itertuples():
        g.add_node(int(row.node), position=(row.longitude, row.latitude))
    for row in pd.read_csv(path/'edges.csv', float_precision='round_trip').itertuples():
        g.add_edge(int(row.source), int(row.target), weight=row.weight)
    return g


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path, help='data/derived/{full,holdout}/REGION')
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--realizations', type=int, default=0, help='200 for the full ensembles')
    p.add_argument('--config', type=Path, default=Path('configs/paper.yaml'))
    args=p.parse_args()
    config=yaml.safe_load(args.config.read_text())
    observed=load_graph(args.input)
    memberships=None
    if (args.input/'fixed_memberships.csv').exists():
        memberships=pd.read_csv(args.input/'fixed_memberships.csv')
        memberships=memberships.loc[memberships.source_event != memberships.event]
    rows=[]
    tasks=[('observed',-1)]+[(model,i) for i in range(args.realizations) for model in ['M_RW','M_SR']]
    args.output.mkdir(parents=True,exist_ok=True)
    for model,i in tasks:
        settings=config['null_models']
        seed=settings['seed']+i+(100000 if model=='M_SR' else 0)
        if model=='observed': g=observed
        elif model=='M_RW':
            g=rewire_degree_preserving(observed,swaps_per_edge=settings['rw_swaps_per_edge'],seed=seed)
        else:
            g=rewire_spatially_constrained(observed,swaps_per_edge=settings['sr_swaps_per_edge'],
                n_distance_bins=settings['distance_bins'],seed=seed)
        stats=summarize_graph(g)
        for eta in config['community']['resolutions']:
            labels,communities=detect_communities(g,resolution=eta,seeds=config['community']['seeds'])
            row=dict(model=model,realization=i,eta=eta,Q=modularity(g,communities,resolution=eta),
                     communities=len(communities),**stats,**g.graph)
            if memberships is not None:
                row.update(evaluate_sample(memberships.loc[np.isclose(memberships.eta,eta)],labels))
            rows.append(row)
        pd.DataFrame(rows).to_csv(args.output/'statistics.csv',index=False)
        print(model,i,flush=True)
    (args.output/'settings.json').write_text(json.dumps(config,indent=2))

if __name__=='__main__': main()
