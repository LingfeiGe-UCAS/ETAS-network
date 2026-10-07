import networkx as nx
import numpy as np
import pytest
from fault_etas_network.communities import detect_communities, modularity
from fault_etas_network.samples import freeze_sample, evaluate_sample
from fault_etas_network.null_models import rewire_spatially_constrained, rewire_degree_preserving, distance_matrix
from fault_etas_network.construction import build_directed_graph, symmetrize


def test_best_restart():
    g=nx.karate_club_graph()
    seeds=[12345,1,2,3]
    _,best=detect_communities(g,seeds=seeds)
    assert modularity(g,best)==max(modularity(g,detect_communities(g,seed=s)[1]) for s in seeds)


def test_fixed_memberships_and_no_source_inflation():
    mapping=np.array([0,1,2,3])
    sample=freeze_sample({0:{0,1,2},3:{3}},mapping,{0:0,1:0,2:0,3:1},3)
    assert len(sample)==2
    first=evaluate_sample(sample,{0:0,1:0,2:0,3:1})
    second=evaluate_sample(sample,{0:0,1:1,2:1,3:1})
    assert first['retention']==1 and second['retention']==0
    assert first['downstream_memberships']==second['downstream_memberships']==2
    with pytest.raises(KeyError): evaluate_sample(sample,{0:0})


def test_self_loops_only_in_directed_graph():
    d=build_directed_graph(np.array([[.2,.3],[0,.1]]))
    assert nx.number_of_selfloops(d)==2
    assert nx.number_of_selfloops(symmetrize(d))==0


def test_spatial_constraints_and_budget():
    g=nx.watts_strogatz_graph(20,4,.3,seed=2)
    for n in g: g.nodes[n]['position']=(100+n*.1,30+(n%3)*.1)
    for i,(u,v) in enumerate(g.edges): g[u][v]['weight']=(i+1)/50
    null=rewire_spatially_constrained(g,n_distance_bins=2,swaps_per_edge=2,seed=8)
    assert dict(g.degree())==dict(null.degree())
    assert null.graph['accepted_swaps']==2*g.number_of_edges()
    dist=distance_matrix([g.nodes[n]['position'] for n in sorted(g)])
    cuts=np.unique(np.quantile(np.array([dist[u,v] for u,v in g.edges],float),[0,.5,1])[1:-1])
    def values(graph):
        bins={}
        for u,v,d in graph.edges(data=True):
            bins.setdefault(int(np.searchsorted(cuts,dist[u,v],side='right')),[]).append(d['weight'])
        return {k:sorted(v) for k,v in bins.items()}
    assert values(g)==values(null)


def test_unreachable_budget_rejected():
    with pytest.raises(RuntimeError,match='realization rejected'):
        rewire_degree_preserving(nx.complete_graph(5),swaps_per_edge=1,seed=1)
