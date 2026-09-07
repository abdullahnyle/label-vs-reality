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
overview IDs. It imports every column as text to preserve the raw quantity strings.
It saves file names, hashes, row counts and the supplied date in ImportManifest.
An unsuccessful import is discarded. Existing databases are never overwritten.

## From a saved SQLite database

Close DB Browser or another writer after saving the database. The analysis needs:

| Table | Required columns |
|---|---|
| ProductOverview | DSLD ID, Product Name, Market Status, Suggested Use |
| DietarySupplementFacts | DSLD ID, Ingredient, Amount Per Serving, Amount Per Serving Unit |

Extra columns are preserved in the source evidence export. The facts table must
be an ordinary SQLite rowid table, as produced by DB Browser and this loader.
Do not rename unfamiliar fields speculatively; inspect the actual export first.
Existing databases do not need the old hand-built reference tables.

```sh
python scripts/analyze.py data/supplements.db results/local-run --dataset-label "DSLD original snapshot"
```

The reader validates joins and fingerprints the database. Without ImportManifest,
the original CSV hashes and acquisition date remain unknown. The run records that
absence rather than manufacturing provenance.

Use a new output directory for each analysis. Read report.md, parsing.csv,
unmatched_names.csv and sensitivity.csv before treating an output as a finding.
Complete source-panel and candidate reviews separately. Keep raw data and local
runs out of commits; publish only deliberately reviewed, appropriately described
outputs. The .gitignore rules allow small reviewed CSVs under results/published/.
