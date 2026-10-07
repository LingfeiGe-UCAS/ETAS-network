from pathlib import Path
import pandas as pd
import numpy as np
import pytest
from fault_etas_network.io import load_inputs


def test_distance_screening_preserves_catalog(tmp_path):
    pd.DataFrame(dict(event_id=[0,1,2],time=[0.,1.,2.],magnitude=[5.,3.,3.],
                      cell_id=[0,0,0],fault_distance_km=[17.,18.,18.01])).to_csv(tmp_path/'events.csv',index=False)
    pd.DataFrame(dict(source=[0,1],target=[1,2],probability=[.2,.3])).to_csv(tmp_path/'event_pairs.csv',index=False)
    pd.DataFrame(dict(cell_id=[0],longitude=[100.],latitude=[30.])).to_csv(tmp_path/'cells.csv',index=False)
    result=load_inputs(tmp_path,maximum_fault_distance_km=18)
    assert result['event_to_cell'].tolist()==[0,0,-1]
    assert len(result['time'])==3
    assert result['target'].tolist()==[1,2]


def test_missing_distances_requires_explicit_confirmation():
    path=Path(__file__).resolve().parents[1]/'data/example'
    with pytest.raises(ValueError,match='prefiltered'):
        load_inputs(path,maximum_fault_distance_km=18)
    assert len(load_inputs(path,maximum_fault_distance_km=18,prefiltered=True)['time'])>0
