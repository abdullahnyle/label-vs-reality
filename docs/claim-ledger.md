# Claim ledger

Evidence states used here:

- **Implemented and fixture-tested:** code ran on deliberately constructed examples.
- **Historical local observation:** reported in earlier work, not reproduced with the current pipeline.
- **Source-supported:** backed by the linked external reference.
- **Pending review:** requires the real snapshot or label inspection.

## Current implementation

| Claim | Evidence | Status |
|---|---|---|
| Conversion precedes minimum/maximum selection | sql/04_creatine_analysis.sql; mixed mg/g regression in tests/test_analysis.py | Implemented and fixture-tested |
| Each matched ID contributes one summary record | Runtime cardinality check; tied-amount fixture | Implemented and fixture-tested |
| Unparseable quantities are retained as unresolved | scripts/amounts.py; parsing fixtures and exports | Implemented and fixture-tested |
| Original fields and selected-row lineage are exported | source_labels.jsonl export; integration test | Implemented and fixture-tested |
| Runs preserve the input database and reproduce ordered exports | Full-run integration test using a synthetic CSV snapshot | Implemented and fixture-tested |
| Current dataset results and manual classifications are validated | No original snapshot or completed audit supplied for this implementation | Pending review |

## Historical numbers awaiting reconciliation

These figures were reported before the current rebuild. Their arithmetic is
consistent, but the earlier SQL had executable-scope and pre-conversion ranking
problems. The effect on the real counts is unknown until the original data are run.
Do not force the new outputs to match this table.

| Earlier observation | Reported value | Current evidence status |
|---|---:|---|
| ProductOverview rows and distinct IDs | 214,780 each | Historical local observation |
| Ingredient-matched IDs across market statuses | 2,163 | Historical local observation |
| On-market matched IDs | 1,278 | Historical local observation |
| On-market maximum amount at least 3 g | 648 | Historical local observation |
| On-market below 3 g | 268 | Historical local observation |
| On-market unusable amount | 362 | Historical local observation |
| At least 3 g among usable records | 648 / 916 = 70.7% | Arithmetic checked; inputs await rerun |
| Unusable among the full on-market cohort | 362 / 1,278 = 28.3% | Arithmetic checked; inputs await rerun |
| Below-threshold names without creatine | 224 / 268 = 83.6% | Historical local observation; no taxonomy inference |
| Below-threshold names containing creatine | 44 | Historical local observation |
| Candidate format split | 18 other/single-serving, 26 capsule | Pending row-level evidence |
| Populated Suggested Use | 1,196 / 1,278 = 93.6% | Historical local observation |
| Earlier Suggested Use sample | 30 entries, seed not recorded | Original sample membership unavailable |

## Interpretation boundaries

The daily maintenance reference is supported by
[Kreider et al. (2017)](https://doi.org/10.1186/s12970-017-0173-z). Applying a numerical
threshold to per-serving labels does not establish daily adequacy or effectiveness.
A maximum of at least 3 g does not mean that an amount lies within 3–5 g.

A name without “creatine” does not establish an irrelevant product category.
The previously used contamination and manufacturer-intent explanations have been
withdrawn. Differences between market-status groups are descriptive, not evidence
about why products were discontinued. A 2.5 g grouping remains a pattern to check.

The magnesium rows for ID 239649 were reported as indistinguishable in selected
fields. Full source-panel interpretation remains unresolved. Elemental magnesium
fractions are not applied to label amounts.

## Updating this ledger

When data are available, record the dataset hash, analysis code hashes, exact output
and row/filter behind each empirical claim. Document count changes and their causes.
Manual classifications need a reviewer, date and evidence. A successful rerun can
be described as reproduced on the identified snapshot; it is not independent
scientific validation merely because a different assistant ran it.

Earlier notes are retained in docs/history/ for traceability and are superseded by
this ledger and the current methodology.
