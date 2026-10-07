# Reproducibility and provenance

## What this release reproduces

1. Synthetic input -> cumulative/normalized directed network -> communities and cascades.
2. Prepared event-pair probabilities and cell assignments -> observed/null analyses.
3. Bundled final derived graphs -> the manuscript's observed Q, community counts and
   source-excluded holdout retention. This is the preferred exact verification route.
4. Final per-realization summary statistics are in results/reference/M_RW and M_SR.

This is not a raw-catalog-to-ETAS fitting package. It does not estimate catalog
completeness, download source catalogs, reconstruct fault traces or fit ETAS.
Supplying new probabilities is not equivalent to reproducing the fitted manuscript inputs.

## Why the fixed membership file matters

The final experiment inherited eligible sources and memberships from a prior audit
whose observed eligibility partition used seed 12345. Those memberships stayed
fixed when best-of-20 Louvain evaluation was introduced. Re-selecting eligibility
using the best-of-20 partition can therefore change the sample.

The archived membership CSV retains the original source rows for provenance;
evaluation explicitly removes rows where source_event == event. Overlapping
cascades count the same event once per source, not once in the entire catalog.
Missing training-node labels are excluded when freezing the sample, never separately
for individual null realizations. Sources with no evaluable downstream events
contribute nothing to the fraction; source_events in new output counts contributors.

For prepared inputs, --fixed-memberships validates IDs against the supplied mapping.
Do not combine an archived membership file with reindexed events or nodes.
The bundled graph replay does not require raw event catalogs.

## Numerical provenance

data/derived/provenance.json records hashes of the original local graph artifacts.
The accepted-swap kernel is copied from the final experimental implementation.
Distance matrices use float32 as in that implementation; bin cuts use observed
edge-distance quantiles. Repeated distances may prevent exactly equal bin counts.
RW and SR use seed 20260916 + realization, with a 100000 offset for SR.
The same 20 Louvain seeds are used for every graph; retention never selects the run.
Each realization starts afresh from the observed network.

NetworkX 3.1 was used for the final experiments. Node/edge insertion order, library
versions, float serialization and seed order matter for stochastic reproducibility.
CSV edge weights are read with round-trip precision in the archive replay.

## Reference result fields

summary.csv: observed value, null mean, p025, p975, p_ge and p_le.
best_partitions_statistics.csv: selected partition statistics for each realization.
diagnostics.csv: accepted/proposed swaps, acceptance and structural diagnostics.
Legacy reference tables contain both retention (source included) and
downstream_retention (source excluded). **Use downstream_retention for the revised paper.**
The new command output uses retention for source-excluded retention only.

The archive contains existing 200-realization results; release preparation does not
rerun all 200 realizations. verify_reference.py checks observed results directly.
The data/derived folder contains symmetrized loop-free graphs, not the directed
networks needed for degree/edge-weight/out-strength distribution figures.

## Environment and privacy

No private filesystem paths are required at runtime. Install from a clean checkout.
The Python fallback for the Numba kernel is slow. Full ensembles should use Numba.
Do not upload raw catalogs or third-party fault files without checking redistribution rights.
