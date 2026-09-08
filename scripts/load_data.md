# Loading a DSLD snapshot

Use an existing saved database if the objective is to reconcile the original
results. A fresh download is a new dataset and must have a different snapshot name.
The old notes report 214,780 ProductOverview rows across eight batches. Neither
number is a universal requirement for later DSLD downloads.

## From the original CSV files

Download/export the CSV tables from [DSLD](https://dsld.od.nih.gov) if needed, then
extract them into `data/dsld/extracted`. Keep the archive and record when it was
acquired. Do not guess the original date from a file's modification time.

Run from the repository root:

```sh
python scripts/load_data.py data/dsld/extracted data/supplements.db
```

If you know the acquisition date, add `--acquired-on YYYY-MM-DD` with the actual
date. Omit it when unknown. The loader recursively finds files named
`ProductOverview.csv` or `ProductOverview_*.csv`, and the corresponding
`DietarySupplementFacts` files. Do not mix downloads in the input folder.

The loader checks matching batch headers, field counts, blank IDs and duplicate
overview IDs. Strict CSV reading rejects unterminated quoted fields and trailing
text after closing quotes. Valid quoted commas, escaped quotes and multiline
fields remain intact. It imports every column as text to preserve the raw quantity strings.
It saves file names, hashes, row counts and the supplied date in ImportManifest.
An unsuccessful import is discarded. Existing databases are never overwritten.
The final database is linked into place only if the destination is still unused;
this also protects a file created by another process during the import. Use a
filesystem that supports hard links. An unsupported filesystem fails without
replacing the destination. Acquisition dates are validated, not inferred.

## From a saved SQLite database

Close DB Browser or another writer after saving the database. The analysis needs:

| Table | Required columns |
|---|---|
| ProductOverview | DSLD ID, Product Name, Market Status, Suggested Use |
| DietarySupplementFacts | DSLD ID, Ingredient, Amount Per Serving, Amount Per Serving Unit |

Extra columns are preserved in the source evidence export. The facts table must
be an ordinary SQLite rowid table, as produced by DB Browser and this loader.
Facts columns named `rowid` or `source_rowid` are rejected because they would
obscure the source-row identifier in the evidence export. Do not drop or rename
such columns without checking their meaning first.
Do not rename unfamiliar fields speculatively; inspect the actual export first.
Existing databases do not need the old hand-built reference tables.

```sh
python scripts/analyze.py data/supplements.db results/local-run --dataset-label "DSLD original snapshot"
```

The reader validates joins and fingerprints the database. Without ImportManifest,
the original CSV hashes and acquisition date remain unknown. The run records that
absence rather than manufacturing provenance.
Source evidence includes both matched and surrounding nonmatching facts for each
matched label ID, with null values retained in JSON. Neither group is a completed
panel review.

Use a new output directory for each analysis. Read report.md, parsing.csv,
unmatched_names.csv and sensitivity.csv before treating an output as a finding.
Complete source-panel and candidate reviews separately. Keep raw data and local
runs out of commits; publish only deliberately reviewed, appropriately described
outputs. The .gitignore rules allow small reviewed CSVs under results/published/.


## Reproduce the recorded verification

The supplied source ReadMe records `2026-01-10T17:52:06-05:00` for batch 8 and
214,780 downloaded labels. The archive comprises eight files per imported table.
Use `--acquired-on 2026-01-10` for those files; do not infer that date from the
Drive upload or filesystem timestamp.

To compare the original saved database with a fresh CSV import:

```sh
python scripts/verify_snapshot.py data/supplements.db data/original-csv.db results/local-run
```

This prints integrity checks, full-table differences before/after the documented
normalization, source hashes and an independent decimal-arithmetic comparison.
It does not change either source. IDs stored as integers or text use the same
text ordering for the Suggested Use sample, but raw source exports retain their
original types and whitespace. Identical raw exports are promised only for
identical input bytes, not for differently imported copies of the same tables.

`results/published/2026-01-10/` contains selected outputs from the CSV rebuild.
The full surrounding-facts JSONL can be regenerated locally and is not committed
because it is about 21 MB. Candidate context and API excerpts are included for
the reviewed cases. The original 16 CSV hashes are in run.json's import manifest.
