# DSLD snapshot downloaded 10 January 2026

These outputs were regenerated from the original CSV archive. Two complete runs
produced identical files. `source-verification.json` records the comparison with
the supplied SQLite database and an independent check of all matched amounts.

The runner deliberately creates pending review queues. Its `run.json` pending
count describes that generation step. Completed assistant source-text reviews
are separate in `review/`; Abdullah has not yet independently reviewed them.
See ../../../docs/reviews/README.md for coverage and review decisions.

The full generated source-label export is omitted because it contains 21 MB of
surrounding facts. Candidate and checked API context are retained in `review/`.
The original archive and databases remain local. File fingerprints are in
`run.json`; reproduction commands are in ../../../scripts/load_data.md.

The case study explains why per-serving thresholds do not establish daily intake,
clinical effectiveness, or measured contents. The 70.7% maximum-amount result
must be read alongside the 61.0% minimum-amount result and missing quantities.
