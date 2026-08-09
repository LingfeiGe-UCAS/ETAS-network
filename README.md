# Fault-associated ETAS networks

This repository provides a compact, reproducible implementation of the
fault-associated earthquake-network framework developed for the accompanying
manuscript. Event-pair probabilities from a space-time ETAS model are
aggregated onto persistent spatial cells associated with mapped fault systems.
The resulting directed weighted networks support structural, community,
null-model, and cascade-retention analyses.

The public repository contains only the final analysis workflow. Raw catalogs,
third-party fault files, manuscript documents, exploratory scripts, and large
simulation outputs are deliberately excluded.

## Scientific workflow

1. Aggregate event-pair probabilities onto fault-associated cells.
2. Normalize outgoing cell weights by the number of events in each source cell.
3. Construct the directed network and its weighted symmetrized projection.
4. Calculate heterogeneity, clustering, and assortative-mixing statistics.
5. Detect Louvain communities across resolution parameters.
6. Compare observations with degree-preserving and spatially constrained nulls.
7. Measure whether recursively connected event sequences remain in the source
   community, including temporal-holdout applications.

## Installation

Using Conda:

```bash
conda env create -f environment.yml
conda activate fault-etas-network
```

Or using an existing Python 3.10 or newer environment:

```bash
python -m pip install -e .
```

## Quick verification

The bundled data are synthetic and are intended only to verify the workflow.

```bash
python scripts/run_example.py
```

The command writes a directed network and a compact JSON summary to
`results/example/`. Run the tests with:

```bash
python -m pytest
```

## Analyze prepared regional data

Prepare `events.csv`, `event_pairs.csv`, and `cells.csv` as described in
[`docs/data_format.md`](docs/data_format.md), then run:

```bash
python scripts/run_paper_analysis.py data/private/REGION \
  --config configs/paper.yaml \
  --output results/REGION
```

`configs/paper.yaml` records the principal thresholds, community resolutions,
null-ensemble settings, and random seed used in the manuscript. The lightweight
regional entry point produces observed network, community, and retention
results. The null-model functions can be imported from
`fault_etas_network.null_models` for full ensembles.

For the nonoverlapping temporal evaluation, run:

```bash
python scripts/run_temporal_holdout.py data/private/REGION \
  --config configs/paper.yaml \
  --output results/REGION/temporal_holdout.json
```

The two rewiring ensembles can be reproduced with:

```bash
python scripts/run_null_ensembles.py data/private/REGION \
  --config configs/paper.yaml \
  --output results/REGION/null_ensembles.csv
```

Use `--realizations 2` for a quick diagnostic; the paper configuration uses
200 realizations. Add `--temporal-holdout` to construct communities from the
earlier catalog interval and evaluate the two null models with later cascades.

## Repository map

| Path | Purpose |
|---|---|
| `src/fault_etas_network/` | Reusable scientific implementation |
| `scripts/` | Executable example and regional-analysis entry points |
| `configs/paper.yaml` | Versioned manuscript parameters |
| `data/example/` | Small synthetic smoke-test data |
| `tests/` | Tests of the main mathematical operations |
| `docs/` | Input schema and reproducibility guidance |

## Reproducibility levels

- **Smoke test:** the bundled synthetic example runs in seconds.
- **Observed regional analysis:** prepared ETAS probability and cell-assignment
  inputs reproduce network, community, and retention summaries.
- **Full paper reproduction:** licensed inputs, null-model ensembles, and figure
  source tables are deposited separately on Zenodo to avoid placing large or
  restricted files in GitHub.

See [`docs/reproducibility.md`](docs/reproducibility.md) for details.

## Data and licensing

The software is released under the MIT License. The synthetic example data are
CC0. Third-party earthquake catalogs and fault databases retain their original
licenses and are not covered by the software license. See
[`data/README.md`](data/README.md) before depositing regional inputs.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Before the
first public release, replace the placeholder GitHub account, add all software
authors and ORCID identifiers, archive release `v1.0.0` with Zenodo, and insert
the resulting DOI into both files.

Suggested software citation:

> Ge, L. (2026). Fault-associated ETAS networks (Version 1.0.0) [Software].
> Zenodo. https://doi.org/10.5281/zenodo.TODO

## Development and archived versions

- Development repository: `https://github.com/USERNAME/fault-associated-etas-networks`
- Archived release: `https://doi.org/10.5281/zenodo.TODO`

Please open an issue for reproducibility problems and include the software
version, operating system, Python version, configuration file, and random seed.
