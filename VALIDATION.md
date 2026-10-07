# Release validation

Prepared 2026-10-07. No GitHub push or Zenodo publication performed.

- 12 unit tests cover distance screening, construction, chronological split, cascades, fixed samples,
  best-of-restarts selection, spatial constraints and incomplete-swap rejection.
- Synthetic observed, holdout and two-realization null command-line runs pass.
- Eight archived observed graphs verified: 48 Q/community-count cases and
  24 source-excluded holdout retention cases agree with final saved calculations
  to absolute tolerance 1e-12.
- Four null graph spot checks (Shanxi full/holdout, M_RW/M_SR, realization 30)
  exactly match archived edges, weights, accepted swaps and proposal counts.
- Full 200-realization ensembles were not recomputed for release preparation;
  the included reference tables are copied from the completed final runs.

The tiny synthetic example uses one distance bin because its sparse graph cannot
complete a two-bin swap. Nontrivial distance-bin preservation is tested separately.
This smoke setting must not be confused with the paper's ten-bin configuration.

Use scripts/verify_reference.py for repeatable observed-result checks.
Library versions and insertion order can affect Louvain solutions; use NetworkX 3.1
for matching the manuscript. Package preparation retained the existing MIT software
license and did not expand third-party catalog or fault-data redistribution rights.
