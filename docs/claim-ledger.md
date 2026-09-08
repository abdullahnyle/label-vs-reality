# Claim ledger

This ledger supersedes earlier notes in `docs/history/`. The current source is the
10 January 2026 DSLD CSV download, reconciled with the supplied saved database.

| Claim | Evidence | Status |
|---|---|---|
| 214,780 overview rows and 2,020,130 facts rows | Published source-verification.json and run.json | Reproduced; both databases pass integrity checks |
| 2,529 matched rows; 2,163 matched IDs | matched_rows.csv; independent Decimal check | Reproduced on both inputs |
| 1,278 on-market IDs: 648 at least 3 g, 268 below, 362 unusable | records.csv; expanded/on_market/max/3 row in sensitivity.csv | Reproduced |
| 70.7% among 916 usable IDs; 28.3% missing in full cohort | Same tables | Reproduced arithmetic; not an efficacy measure |
| Minimum selection gives 559 / 916 = 61.0% | expanded/on_market/min/3 sensitivity row | Reproduced; 89 threshold changes |
| Explicit-wording comparison gives 648 / 911 = 71.1% | explicit_monohydrate/on_market/max/3 | Reproduced; wording does not establish chemistry |
| Case-insensitive comparison gives 668 / 957 = 69.8% | case_insensitive/on_market/max/3; case_variants.csv | Reproduced; original list is not exhaustive |
| 224 below-threshold names lack creatine; 44 contain it | records.csv name_group | Reproduced naming split only |
| 1,196 / 1,278 Suggested Use entries populated | records.csv | Reproduced, 93.6%; populated does not mean readily interpretable |
| Candidate forms: 25 capsules, 16 powders, two liquids, one wafer | candidate_review.csv; candidate_context.jsonl | Source-text review completed; replaces earlier 26/18 claim |
| Candidate daily amounts are defensible for every label | Candidate decisions leave unclear entries blank | Not claimed; estimates are conditional on explicit recorded schedules |
| 58 API labels agree on matched amounts | api_checks.csv; api_context.jsonl | Checked against retrieved API responses; not independent source validation |
| Seven scanned labels inspected | docs/reviews/image-checks.csv | Targeted visual review, including two discrepancies |
| The entire cohort is verified against original images | Only seven images reviewed | Not claimed |
| Every creatine product is captured | Omitted names remain in unmatched_names.csv | Not claimed |
| Products without creatine in the name are contamination | No supporting taxonomy | Withdrawn |
| The original unseeded 30-entry sample is reproduced | Membership was never retained | Not claimed; new seeded sample reviewed separately |

All result filenames above are under `results/published/2026-01-10/`, with review
outputs in its `review/` folder. `run.json` records code/configuration hashes and
all 16 CSV fingerprints. `source-verification.json` records the saved and rebuilt
database hashes. The code tests cover synthetic failure cases; the real-data
reconciliation is a separate check.

The [ISSN reference](https://doi.org/10.1186/s12970-017-0173-z) discusses daily
maintenance intake. The study's 3 g screen describes recorded amounts per serving;
it does not establish effectiveness, intake, chemical identity or actual contents.

Source discrepancy 337727 is retained unchanged in the primary outputs. Omitting
it alone produces 648 / 915 = 70.8%; this is a limited sensitivity check, not an
estimate of every possible source error. The serving-metadata issue at 551 does
not alter its amount classification.

Reviews identify ChatGPT assistance and Abdullah's pending review. Nothing here
asserts that Abdullah personally checked evidence he has not yet reviewed.
Magnesium remains exploratory and its old duplicate question remains unresolved.
