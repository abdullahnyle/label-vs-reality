# Label vs. Reality

A reproducible study of creatine amounts recorded in NIH's Dietary Supplement
Label Database (DSLD). It asks how much the answer depends on ingredient matching,
serving selection and missing data, then checks selected records against their
source labels.

## What the data show

In the 10 January 2026 download, the original 25-name ingredient list matches
2,163 label IDs. Of the 1,278 marked on-market, 916 have a usable amount and 362
have none. Using each label's largest usable recorded amount, **648 of 916
(70.7%) reach 3 g**. Using the smallest, **559 of 916 (61.0%) do**.

Those percentages describe recorded amounts. They do not measure effectiveness,
actual contents or what someone takes daily. The missing 362 labels are 28.3% of
the on-market cohort, and distinct label IDs are not necessarily distinct products.

| Comparison | At least 3 g / usable labels | Share |
|---|---:|---:|
| Original names, maximum amount | 648 / 916 | 70.7% |
| Original names, minimum amount | 559 / 916 | 61.0% |
| Explicit-monohydrate names only, maximum | 648 / 911 | 71.1% |
| Case-insensitive original names, maximum | 668 / 957 | 69.8% |

Case-insensitive matching adds 92 on-market IDs. The original list also omits
other formulations and spellings; neither comparison represents every creatine
product. The [case study](docs/creatine-case-study.md) explains the cohort and
links each result to its evidence.

![Recorded label amounts](results/published/2026-01-10/amounts.svg)

## What changed after checking the sources

The rebuilt pipeline reproduces the earlier 70.7% exactly. That supports the
calculation, but the source review narrows its meaning:

- 89 on-market labels cross the threshold depending on minimum versus maximum
  serving selection.
- The 44 named, below-threshold candidates contain 25 capsule, 16 powder, two
  liquid and one wafer records. The earlier 26/18 split was wrong.
- A scanned label lists 2.5 g per two capsules, with instructions for those two
  capsules at three meals. Another lists 2.8 g per four capsules taken once daily.
  Capsule format alone cannot explain a below-threshold record.
- Two scanned records expose serving metadata or numeric-notation discrepancies.
  The raw data are retained, with the problems documented separately.

The earlier interpretation that names without “creatine” represented contamination
has been withdrawn. Blends can legitimately contain monohydrate. This study does
not infer manufacturer intent or add together different creatine-compound masses.

## Evidence and reproducibility

The original database and a fresh import of all 16 source CSVs agree across
214,780 overview rows and 2,020,130 facts rows after accounting for storage types,
blank values and surrounding whitespace. Both pass SQLite integrity checks. An
independent decimal-arithmetic check agrees with all 2,163 matched label summaries.

The review includes 44 candidate text records, a reproducible 30-record Suggested
Use sample, 58 live API comparisons and seven scanned-label checks. The automated
API comparisons agree on matched amounts; agreement with an API is not image
validation. Reviews were performed with ChatGPT assistance and await Abdullah's
own review. This is a descriptive case study, not a fully adjudicated product audit.

- [Results and row-level exports](results/published/2026-01-10/)
- [Method and limitations](docs/methodology.md)
- [Claim ledger](docs/claim-ledger.md)
- [Source review and image evidence](docs/reviews/README.md)
- [Preparation notes](docs/defending-the-analysis.md)

## Run it

Use Python 3.10+ with SQLite 3.25+; no third-party Python packages are required.
Keep the original CSV batches together in an otherwise empty folder.

```sh
python scripts/load_data.py data/dsld/original-csv data/original-csv.db --acquired-on 2026-01-10
python scripts/analyze.py data/original-csv.db results/local-run --dataset-label "DSLD CSV download 10 January 2026"
python -m unittest discover -s tests -v
```

The date above belongs to the supplied download's ReadMe. Use the actual date for
a different snapshot. A fresh download may not reproduce these counts. The
[loading guide](scripts/load_data.md) covers saved databases and provenance.

SQL handles matching, aggregation and serving selection. Python validates quantity
text and exports the evidence. The runner opens the input read-only and refuses to
overwrite an existing run. Its generated review queues start pending; completed
review files are kept separately.

## Scope and sources

The 3 g threshold is motivated by the daily maintenance reference in
[Kreider et al. (2017)](https://doi.org/10.1186/s12970-017-0173-z). That daily reference
does not validate a per-serving effectiveness claim. Amounts above 5 g also count
as “at least 3 g”; the category is not the 3-5 g range.

[NIH DSLD](https://ods.od.nih.gov/Research/Dietary_Supplement_Label_Database.aspx)
contains label information, including historical records. Snapshot market status
is not live retail verification. This study cannot establish absorption, clinical
benefit, price/value or national-market prevalence. Full daily-intake extraction
and laboratory testing are outside its scope.

The earlier magnesium SQL remains exploratory. Its chemical fractions are not
applied to labeled magnesium amounts, and the duplicate investigation is unfinished.

## License

Project code and documentation: [MIT](LICENSE). The
[DSLD API specification](https://api.ods.od.nih.gov/dsld/v9/) lists CC0 1.0. Raw
archives and databases are excluded for size. Preserve NIH attribution and snapshot
provenance. The project license does not relicense third-party label images or
trademarks; image reviews link to the source PDFs.
