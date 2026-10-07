# Fault-centric ETAS networks

Version 1.1.0 — submission update.

Code and derived network data accompanying **Fault-Centric ETAS Networks Link
Event-Level Earthquake Dependence to Mesoscale Spatial Organization**.

Event-pair ETAS probabilities are aggregated onto fault-associated cells.
Cumulative contributions are thresholded before source-event normalization.
Directed networks retain self-loops; clustering, communities and rewiring use
the loop-free weighted projection W + W.T.

## Install

Python 3.10 or newer:

```bash
python -m pip install -e ".[test]"
python -m pytest -q
python scripts/run_example.py
```

For the archived manuscript calculations use NetworkX 3.1. Other versions may
change Louvain partitions even with identical seeds. Optional Numba accelerates
rewiring substantially: `python -m pip install numba`.
Without it the same kernel runs in Python but large ensembles will be slow.

## Verify the manuscript's derived networks

The package includes eight derived networks (full and training-period networks
for Shanxi, Italy, Chuan–Dian and Southern California), frozen holdout memberships,
and final RW40/SR640 reference tables. INGV is the internal directory name for Italy.

```bash
python scripts/verify_reference.py
python scripts/run_archived_graph.py data/derived/holdout/INGV --output results/check_italy
```

The verification compares all 48 observed modularity/community results and the
24 downstream-retention results against the saved final experiments.

To regenerate null realizations for a derived graph:

```bash
python scripts/run_archived_graph.py data/derived/full/INGV --realizations 200 --output results/italy_null
```

This can take substantial time. The command is serial and does not automatically
occupy all CPU cores. Existing reference tables are under `results/reference/`.
See [reproducibility notes](docs/reproducibility.md) before claiming exact reproduction.

## Analyze new prepared inputs

Prepare the CSV files described in [data format](docs/data_format.md). ETAS fitting,
distance-to-fault calculation and assignment to 6 km fault-associated cells take
place upstream. If events.csv includes fault_distance_km, the commands enforce
the configured 18 km limit before network aggregation. Without that column,
--prefiltered is required to confirm that upstream processing already applied it.
Screening does not remove catalog rows, change event IDs, or refit ETAS.

```bash
python scripts/run_paper_analysis.py data/private/REGION --output results/REGION
python scripts/run_temporal_holdout.py data/private/REGION --output results/REGION/holdout
python scripts/run_null_ensembles.py data/private/REGION --temporal-holdout --realizations 200 --output results/REGION/holdout_null
```

All `--output` arguments now designate directories, not JSON filenames.
Use `--fixed-memberships PATH` to supply a saved sample with matching event/node IDs.
Otherwise eligibility is determined once per resolution using the original
audit seed (12345), then frozen before best-of-20 evaluation and all null runs.

## Final analysis settings

- Cumulative cell-pair threshold: 0.001; downstream probability threshold: 0.1.
- Resolutions: 0.1, 0.5, 1, 1.5, 2, 3.
- Louvain seeds: 12345, then 1–19; highest Q retained, first run on exact ties.
- Each null starts from the observed graph: 200 realizations per model.
- M_RW: 40 accepted swaps per edge, followed by global weight permutation.
- M_SR: 640 accepted swaps per edge; 10 equal-frequency distance bins;
  weights retain their distance-bin affiliation during swaps.
- Rejected proposals do not count. Unmet swap budgets raise an error.
- Retention excludes each source itself, uses fixed downstream memberships,
  and does not reapply the community-size criterion to randomized partitions.
- Null summaries report means, central 95% intervals and plus-one tail probabilities.

Increasing swap counts was checked in the research workflow; these settings are
not a mathematical proof of uniform mixing. The nulls do not preserve node strengths.

## Scope and licensing

The code is MIT licensed; bundled synthetic data are CC0. Raw earthquake catalogs,
third-party fault traces, manuscript documents, credentials and exploratory outputs
are not included. Derived graph positions are cell locations, not raw fault traces.
No blanket relicensing of third-party source data is implied.
See [data notes](data/README.md) and [changes](CHANGELOG.md).

## Citation and archive

Development: https://github.com/LingfeiGe-UCAS/ETAS-network

Previous published version (1.0.1): https://doi.org/10.5281/zenodo.21860394

**The 1.1.0 archive DOI has not yet been assigned.** Do not cite the previous DOI
as if it identifies this update. After archiving, insert the new version DOI and
publication date into CITATION.cff and update the manuscript's availability statement.
