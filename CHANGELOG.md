# Changes

## 1.1.0 — submission update, prepared 2026-10-07

- Align rewiring with final accepted-swap implementation (RW40/SR640).
- Preserve spatial-bin weight affiliation during swaps; remove post-SR reshuffling.
- Require completion of the accepted-swap budget.
- Evaluate best-of-20 Louvain partitions with identical seed lists.
- Freeze holdout memberships before null comparisons; exclude source events.
- Add final full/training derived networks, reference statistics and replay verification.
- Retain self-loops in directed construction, remove them in the projection.
- Add connected-component output, coverage counts and central 95% null summaries.
- Remove assortativity from the default metric summary.
- Add input validation and regression tests.
- Replace separate legacy runners with a shared workflow; outputs are directories.
- New archive DOI and release date remain unset until publication.

This package was prepared from the local release source and final experiment files,
then checked against GitHub commit 53b70a1 before upload. Existing author and
repository metadata are preserved; the previous archive DOI is labeled explicitly.
- Enforce the configured 18 km cutoff when fault_distance_km is supplied; otherwise
  require explicit --prefiltered confirmation of upstream screening.
