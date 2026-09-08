# Creatine amounts: a snapshot replication and source audit

## Question

How do recorded creatine amounts compare with a 3 g threshold, and how much does
the answer depend on the data and analysis choices?

The project began with a stronger interpretation about effective doses. That
interpretation did not survive scrutiny of the measurement. The database contains
label declarations, the reference concerns daily intake, and the analysis selects
amounts recorded per serving. Reproducing a percentage does not close those gaps.

## Data and reconstruction

The source is a DSLD download dated 10 January 2026. Its ReadMe reports 214,780
labels. Eight ProductOverview CSVs contain 214,780 rows; eight facts CSVs contain
2,020,130 rows. A read-only run on the saved database and a fresh CSV import
reproduce the same historical cohorts and amount categories.

The saved database uses integer/numeric storage and trims some strings. The CSV
loader retains text. Comparing all rows in original order finds no differences
after accounting for these storage types, blank values and surrounding whitespace.
Both databases pass integrity checks and retain their original hashes after
analysis. A separate Decimal calculation agrees with the production pipeline on
all 2,163 matched labels and their minimum/maximum amounts. These checks establish
computational agreement, not the truth of every source declaration.

The database and CSV hashes are in [source-verification.json](../results/published/2026-01-10/source-verification.json)
and [run.json](../results/published/2026-01-10/run.json). The original data are large
and remain outside Git; the commands in the loading guide recreate the analysis
when those files are available.

## Main result and its denominator

The original 25 ingredient names match 2,529 rows belonging to 2,163 distinct label
IDs. Of these, 1,278 are marked on-market and 885 off-market in the snapshot.

| On-market classification, using maximum usable amount | Label IDs |
|---|---:|
| At least 3 g | 648 |
| Below 3 g | 268 |
| No usable amount | 362 |
| Total | 1,278 |

The reported 70.7% is 648 / 916 usable IDs. The missing 362 IDs are 28.3% of the
full on-market cohort. Two otherwise usable on-market labels also contain
unresolved declarations, so their observed maxima do not resolve every row.

This exactly reproduces the earlier figures. Fixing executable SQL scope and
conversion-before-selection was necessary for a reliable method, but did not
change these aggregate counts on this snapshot. There is no reason to manufacture
a changed headline to make the debugging sound more consequential.

## Sensitivity is part of the finding

| Rule | On-market IDs | Usable | At least 3 g | Share of usable |
|---|---:|---:|---:|---:|
| Original names, maximum | 1,278 | 916 | 648 | 70.7% |
| Original names, minimum | 1,278 | 916 | 559 | 61.0% |
| Explicit monohydrate wording, maximum | 1,271 | 911 | 648 | 71.1% |
| Case-insensitive original names, maximum | 1,370 | 957 | 668 | 69.8% |

89 labels cross the screen when the serving selection changes, a 9.7 percentage
point difference among usable labels. The scanned label for
[209975](https://api.ods.od.nih.gov/dsld/s3/pdf/209975.pdf) illustrates why: it lists
one scoop, half a scoop and one-third of a scoop with different amounts.

The original exact list misses `CreaPure Creatine Monohydrate` (56 source rows)
and `micronized Creatine Monohydrate` (121). The case-insensitive comparison admits
these two spellings, adding 166 IDs across market statuses and 92 on-market IDs.
It does not automatically include the remaining formulations, mixtures or typos.
The study is explicitly a screen of a defined list, not an exhaustive census of
creatine monohydrate labels. See [coverage decisions](reviews/ingredient-coverage.csv)
and all 72 combinations in [sensitivity.csv](../results/published/2026-01-10/sensitivity.csv).

## What the candidate review establishes

Among the 268 below-threshold on-market records, 44 contain “creatine” in the
product name and 224 do not. That is a naming split, not proof that the 224 are
irrelevant. The 44 candidates contain 25 capsule, 16 powder, two liquid and one
wafer records, replacing the earlier unsupported 26/18 split.

Their recorded directions were read and coded individually. Where units and
frequency were clear, the review calculates an explicitly limited daily amount
for the stated phase. Where frequency, serving basis or source data were unclear,
the daily fields remain blank. These are interpretations of instructions, not
recommendations to take the products.

Examples checked against the scanned labels:

| Label ID | What the source shows | Implication |
|---|---|---|
| [57461](https://api.ods.od.nih.gov/dsld/s3/pdf/57461.pdf) | 2.5 g per two capsules; those two capsules at three meals | 7.5 g across the specified day despite a sub-3-g serving |
| [253763](https://api.ods.od.nih.gov/dsld/s3/pdf/253763.pdf) | 2.8 g per four capsules; four capsules daily | 2.8 g daily, not 11.2 g |
| [328409](https://api.ods.od.nih.gov/dsld/s3/pdf/328409.pdf) | 1 g per two capsules; two capsules twice daily | 2 g across the specified day |
| [64731](https://api.ods.od.nih.gov/dsld/s3/pdf/64731.pdf) | 2.25 g per three capsules; maintenance three to five daily | A 2.25-3.75 g maintenance range; loading is separate |

These examples rule out a blanket explanation based on capsule format. They also
show why below 3 g per serving cannot be translated into ineffective or inadequate.
Other candidates combine different creatine forms; this analysis does not convert
or add their compound masses into a claim about total creatine.

## Source errors that arithmetic cannot repair

[337727](https://api.ods.od.nih.gov/dsld/s3/pdf/337727.pdf) is the most striking case.
The German image has a daily-serving table with `6.400 mg` and `3.200 mg`; its
CSV and live API encode 6.4 mg and 3.2 mg with four/two-capsule mappings. The printed
notation and daily-serving headings indicate a separator and serving-basis
problem. The review records it without silently substituting a per-serving value.

Removing just this disputed ID, rather than correcting it, gives 648 / 915 =
70.8% among usable on-market records. This small change does not estimate the
prevalence or overall impact of transcription errors.

[551](https://api.ods.od.nih.gov/dsld/s3/pdf/551.pdf) records 4,200 mg correctly,
but its facts serving field says one capsule while the image and overview say six.
That does not change this amount threshold classification. It would matter for
a daily-intake calculation based on facts serving metadata.

## Review coverage and limits

The source audit covers all 44 candidate texts, a new seeded 30-record Suggested
Use sample, 58 API comparisons and seven images. The additional 14 API cases were
selected to cover unnamed products on both sides of the threshold, missing and
partly missing amounts, and multiple serving rows. All 58 comparisons agree on
matched amounts. The API is another representation of the same database, not an
independent assay or a substitute for the label image.

The 30-record sample contains fixed schedules, ranges, loading/maintenance phases,
workout-only directions and unspecified frequencies. It does not establish that
automatic extraction is impossible. Its membership is reproducible using a fixed
seed and textual ID ordering; it is not a reconstruction of the earlier unseeded
sample. Full daily-intake extraction remains outside this study.

Review decisions are assistant-assisted, individually recorded and open to
Abdullah's review. Seven targeted images cannot validate every row or establish
an error rate. These data cannot measure actual contents, absorption, adherence,
clinical effectiveness, price/value or national-market prevalence. Market status
belongs to the January snapshot; label versions and package sizes can have separate
IDs. Source images themselves contain manufacturer claims, not independently
verified scientific findings.

The defensible result is a reproduced amount screen with a measured dependence on
method choices and documented source limitations. The strongest contribution is
the traceable path from raw records to a narrower conclusion.
