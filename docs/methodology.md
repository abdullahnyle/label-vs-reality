# Methodology

## Scope and analysis unit

This is a descriptive screen of recorded amounts. Each distinct DSLD ID contributes
one summary record. Several ingredient rows can belong to that ID, including
multiple serving panels and repeated declarations. Different IDs may also refer
to versions of a physical product. This analysis does not merge those versions.

The broad cohort matches the exact, case-sensitive strings in
`config/creatine_aliases.csv`. Keeping that list explicit preserves the earlier
inclusion rule. The `explicit_monohydrate` flag describes wording, not laboratory
confirmation: `Creatine Mono` and `Creatine; Micronized` lack the explicit term.
Both broad and explicit-wording cohorts appear in the sensitivity table. A third
comparison adds only case variants of the original names, without fuzzy matching
or automatically admitting other formulations. It exposes a known coverage gap;
the original cohort stays fixed for historical reconciliation.
`unmatched_names.csv` is a discovery queue, not an automatically included cohort.
Matching and unmatched-name grouping explicitly use binary collation, so a saved
database's case-insensitive column settings cannot silently broaden the cohort.

## Source validation

The loader imports every matching CSV batch in sorted path order, retains all
columns as text and requires identical headers across batches. IDs must be present;
ProductOverview IDs must be unique. Analysis also rejects orphan ingredient rows
rather than silently dropping them at the join. IDs are not inferred from names.
CSV reading uses strict quote handling so an unterminated field or trailing text
after a closing quote cannot silently change the imported content. Valid multiline
fields and escaped quotes are retained.

Original field names, values and row counts remain available. ImportManifest stores
per-file SHA-256 digests and acquisition dates if supplied. For existing databases
without that manifest, acquisition provenance remains unknown even though the
analysis can fingerprint the database. Do not describe a file hash as proof that
the source labels are correct.

## Quantity parsing

Supported units are `mg`, `g` and `Gram(s)`, ignoring surrounding whitespace and
case. Quantities must be positive decimal scalars. Properly grouped thousands
separators are accepted: `3,000 mg` becomes 3 g. Scientific notation, negative
numbers, decimal commas, inequalities, ranges and free text are left unresolved.

Missing amounts, missing units, unsupported units, invalid/non-scalar text and zero
values receive separate status codes. A zero is held for review because it could
be a source placeholder; the code does not infer absence of creatine. When more
than one defect is present, the parser reports the first one in that order. Raw
values remain in matched_rows.csv for further inspection.

The parser is deliberately limited and visible in scripts/amounts.py. Extend it
only after inspecting actual unhandled values and adding a relevant test. There
is no automatic imputation or conversion of blend weight into creatine weight.
Checking whether a matched declaration refers to an individual ingredient or an
entire blend remains a source-panel review task.

## Multiple amounts

Conversion precedes aggregation. The primary quantity is the maximum **usable
recorded** amount within an ID. The minimum is retained for comparison. Neither
quantity represents verified daily intake. Different amounts may reflect serving
options, panel structures or other unresolved differences; the code does not
assume that they are all legitimate alternative servings.

A tie is represented once, choosing the lowest source SQLite rowid for source-row
traceability. The rowid is stable within the fingerprinted database, not a global
DSLD identifier. All matched source rows are exported, including tied rows.

An ID with both usable and unresolved rows retains an unresolved-row count.
Its observed maximum may not be the maximum of every declaration on the label.
No amounts are summed across repeated rows or parent/subingredient declarations.
The report and sensitivity table expose these partly unresolved IDs separately.
`partly_unresolved` is a subset of `usable`, not a fourth mutually exclusive group;
do not add it to the cohort total.

## Categories and denominators

For each ID, maximum usable amount at least 3 g means `at_least_3g`; a smaller
positive amount means `below_3g`; no usable amount means `unusable`. These categories
partition the matched IDs. The at-least-3-g percentage uses the usable denominator;
the report also displays every unusable ID in the full cohort. Missingness is not
assumed to be random.

Market status maps the snapshot's `On Market` and `Off Market` values, ignoring
case and surrounding whitespace. Everything else stays `unknown`. Unknown-status
records appear separately and in the all-status cohort, but not in the on-market
headline. The run manifest preserves all raw market-status values and their counts.
Its raw-value grouping uses binary collation, independently of the source column's
collation. For example, `On Market` and `ON MARKET` remain separate in provenance
even though both map to the same analysis category.

The name split has three categories: contains creatine, does not contain creatine,
and missing name. It is not a validated product taxonomy. Manufacturer intentions
and causes of discontinuation cannot be inferred from these categories.

## Reference and sensitivity

Kreider et al. (2017), [Supplementation protocols](https://doi.org/10.1186/s12970-017-0173-z),
discuss typical 3–5 g/day maintenance after saturation, with some larger athletes
requiring 5–10 g/day. The daily reference and this study's per-serving threshold
have different time bases. The reference table is not an efficacy classifier.

The generated sensitivity table crosses three alias rules, four market populations,
two amount selections and three thresholds (2.5, 3 and 5 g). Every row includes its
cohort, usable and unresolved counts. The 2.5 g comparison is exploratory; it does
not revise the reference to fit the products. No hypothesis test or national-market
confidence interval is implied by these descriptive comparisons.

## Human review

candidate_review_queue.csv contains named, on-market, below-3-g records. All start
as pending. Match selected_source_rowid to matched_rows.csv and source_labels.jsonl,
then inspect the original label. The latter preserves full overview fields and all
matched facts, including any available serving or panel metadata.
It also includes `other_facts`: every nonmatching facts row for that same ID.
These surrounding rows can expose a parent blend or proportional changes across
panels. They are review context, not extra creatine matches. Rows remain in source
rowid order within each group; no panel relationship is inferred automatically.

Copy reviewed rows into a separately versioned audit file; do not fill results by
inference from the product name. Record dosage form, serving basis, evidence,
reviewer and date. If daily directions are interpreted, preserve ranges and phase
conditions. Do not multiply a per-serving amount by the number of capsules when
the serving already comprises several capsules.

Suggested Use sampling takes up to 30 populated on-market records using a fixed
seed of 20260907 over a pool ordered by the text representation of the ID. This keeps
sample membership stable when one SQLite import stores IDs as integers and another
as text. Python's version is recorded. This is a
new repeatable sample, not a reconstruction of the earlier unseeded sample. Its
coding fields start pending. A varied sample does not prove that automated daily
extraction is impossible; that work is simply outside the primary analysis.

Before publishing an empirical result, inspect matched source rows across parsing
statuses and both sides of the threshold, as well as unmatched ingredient names.
The candidate queue alone cannot validate the entire extraction or classify all
products. Any manual sample's coverage must be stated explicitly.

## Reproducibility and remaining limits

run.json records input and implementation digests, import provenance when present,
software versions and source counts. Repeated runs on identical inputs produce
identical ordered exports. New outputs require a new directory so completed reviews
cannot be silently overwritten. The source database is opened read-only; nonempty
journal/WAL files are rejected until the writer is closed and saved/checkpointed.
The writer-file check runs before reading and again before publishing outputs,
alongside the database hash comparison. This detects observed changes, not every
possible concurrent-writer race. Run against a closed, saved snapshot.

The exporter streams an ordered facts query and retains one label's context at a
time. Temporary summary indexes support joins without modifying the source.
`python tests/benchmark_pipeline.py --unindexed` exercises 220,000 synthetic labels
and 2.2 million facts, runs the analysis twice, checks expected amounts, compares
all export hashes and verifies the unchanged database. It is a scale check with
short constructed fields, not a reconstruction of DSLD's real schema or content.

NIH describes DSLD as [label information](https://ods.od.nih.gov/Research/Dietary_Supplement_Label_Database.aspx),
including historical records and updates. This study cannot establish actual
contents, absorption, individual benefit, price/value or national prevalence.
A source label can itself be inaccurate. Snapshot market status is not live
retail verification. Correct arithmetic and successful synthetic tests do not
substitute for running and checking the real data.


## Completed snapshot check

The supplied CSV ReadMe records a download on 10 January 2026 (version 9.4.0).
All eight ProductOverview and eight DietarySupplementFacts files were imported
with per-file hashes. The saved database has numeric storage and trims some fields;
the new importer preserves the CSV strings. An ordered, full-table comparison
found no differences after normalizing storage types, blank values and surrounding
whitespace. Original bytes and these comparison rules are both documented in
`results/published/2026-01-10/source-verification.json`.

The independent quantity check uses Decimal arithmetic over observed numeric
scalars, separately from the production parser and SQL aggregation. It agrees on
all 2,163 matched IDs, row counts, usable counts and minimum/maximum amounts.
It is not a general second parser for arbitrary future quantity text.

The source-text review covers all 44 named, on-market, below-threshold candidates
and the new 30-record sample. Daily quantities in the candidate review are limited
interpretations of the stated schedule and monohydrate amount. Phases are explicit;
missing frequency and the disputed record 337727 have no daily estimate. These
estimates do not revise the primary per-serving screen. They are not consumption
recommendations, a population estimate, or a full daily-intake parser.

Live API checks cover those 44 candidates plus 14 selected records spanning
amount categories, unnamed products, partial missingness and multiple servings.
They compare matched amount multisets, mapping the API's NP placeholder to missing
and the CSV's semicolon-substituted ingredient names to their API equivalents.
Seven source PDFs were visually inspected. API agreement alone cannot validate
serving metadata or label transcription: IDs 337727 and 551 illustrate why.

The original numeric result is a completed snapshot reproduction. The image
review is targeted, not exhaustive. All assistant-assisted classifications remain
open to Abdullah's review and later correction. No fully validated manufacturer
ranking, nationwide estimate or product-effectiveness conclusion is claimed.
