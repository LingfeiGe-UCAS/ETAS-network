# Data

`derived/` contains the eight final symmetrized, loop-free network edge/node
tables and frozen source/event memberships exported from the completed analyses.
These are derived research outputs, not redistributed raw catalogs or fault traces.
Node coordinates denote analysis cells. Event IDs in membership tables are indices,
not provider catalog identifiers. See `derived/provenance.json` and
`docs/reproducibility.md`. Third-party source licenses remain unaffected.

The CSV membership files include source rows for historical provenance; all new
retention calculations explicitly exclude those rows. The derived graphs alone
cannot regenerate directed-network distribution figures or refit ETAS.

`example/` is a small synthetic dataset distributed under CC0 for testing the
workflow. It is not used in the manuscript.

Regional earthquake catalogs and mapped-fault products are not redistributed
here because they originate from multiple providers with distinct access and
licensing conditions. The companion archived data record should contain only
files for which redistribution is permitted, together with provenance,
processing steps, access dates, and provider citations.
