# Reproducibility guide

## Lightweight verification

Run `python scripts/run_example.py`. This exercises every core stage on the
bundled synthetic data and normally finishes within seconds.

## Regional analysis

Prepare a regional directory using `docs/data_format.md`, then run:

```bash
python scripts/run_paper_analysis.py PATH_TO_REGION --output results/REGION
```

The paper settings are recorded in `configs/paper.yaml`. Large null ensembles
and manuscript figure-source files are preserved in the companion Zenodo data
record rather than duplicated in GitHub. Random seeds, ensemble sizes, distance
bins, probability thresholds, and community resolutions must be reported with
every archived run.

## Scope

This release contains the analysis implementation used after event-pair ETAS
probabilities and event-to-cell assignments have been prepared. Raw catalogs,
third-party fault databases, manuscript files, and historical exploratory runs
are intentionally excluded.
