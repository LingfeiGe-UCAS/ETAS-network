"""Verify all archived observed Q/retention results; no long null ensemble required."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from run_archived_graph import load_graph
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.samples import evaluate_sample
from fault_etas_network.metrics import summarize_graph

root=Path(__file__).resolve().parents[1]
config=yaml.safe_load((root/'configs/paper.yaml').read_text())
rows=[]
for path in sorted((root/'data/derived').glob('*/*/observed_reference.json')):
    graph=load_graph(path.parent)
    ref=json.loads(path.read_text())
    metrics=summarize_graph(graph)
    assert abs(metrics['clustering_unweighted']-ref['diagnostics']['C']) < 1e-12
    assert abs(metrics['clustering_weighted']-ref['diagnostics']['Cw']) < 1e-12
    members=None
    if (path.parent/'fixed_memberships.csv').exists():
        members=pd.read_csv(path.parent/'fixed_memberships.csv')
        members=members.loc[members.source_event != members.event]
    for row in ref['best']:
        eta=row['eta']
        labels,communities=detect_communities(graph,resolution=eta,seeds=config['community']['seeds'])
        q=modularity(graph,communities,resolution=eta)
        assert abs(q-row['Q']) < 1e-12,(path,eta,q,row['Q'])
        assert len(communities)==row['communities'],(path,eta)
        if members is not None:
            r=evaluate_sample(members.loc[np.isclose(members.eta,eta)],labels)
            assert abs(r['retention']-row['downstream_retention']) < 1e-12,(path,eta,r)
        rows.append(dict(scope=path.parent.parent.name,region=path.parent.name,eta=eta,Q=q))
    print(path.parent, 'verified',flush=True)
print(f'PASS: {len(rows)} observed resolution cases; holdout source-excluded retention matched.')
