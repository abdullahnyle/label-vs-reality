# Loading the DSLD snapshot

Keep one download's CSV batches together in their own folder. Mixing downloads
can combine different label versions without making the problem obvious.

From the repository root:

```sh
python scripts/load_data.py data/dsld/original-csv data/supplements.db \
  --acquired-on 2026-01-10
```

The date above belongs to the supplied January 2026 archive. Use the date recorded
with a different download, or omit the option when it is unknown.

The loader finds `ProductOverview*.csv` and `DietarySupplementFacts*.csv`
recursively. It checks that batch headers agree, each row has the expected number
of fields, DSLD IDs are present, ProductOverview IDs are unique and every facts
row belongs to a product record. It retains the CSV values as text so strings
such as `3,000` remain available for review.

`ImportManifest` records each source filename, SHA-256 fingerprint, row count
and acquisition date. The destination must be new. A failed import is discarded,
and a file created at the destination while an import is running is not replaced.

Check the result before analysis:

```sql
PRAGMA integrity_check;
SELECT COUNT(*) FROM ProductOverview;
SELECT COUNT(*) FROM DietarySupplementFacts;
SELECT SUM(rows) FROM ImportManifest GROUP BY table_name;
```

The January archive contains 214,780 ProductOverview rows and 2,020,130 facts
rows. Those counts identify this snapshot; they are not requirements for later
DSLD downloads.

The amount parser accepts positive scalar values in grams or milligrams. Missing
values, ranges, inequalities, zeros and unfamiliar units stay unresolved for
review rather than being converted to zero.

## Matching creatine declarations

With the imported database in place, export the recorded ingredient rows:

```sh
mkdir -p results
python scripts/creatine_matches.py data/supplements.db > results/creatine-exact.csv
python scripts/creatine_matches.py data/supplements.db --ignore-case > results/creatine-case-variants.csv
```

The default uses the 25 names from the historical SQL, matched exactly even if
the input database has a case-insensitive ingredient column. `--ignore-case`
allows ASCII capitalization differences in those same names. It does not use
substring or fuzzy matching. Rows added by this option have `case_variant` in
the `alias_match` column; neither spelling nor quantity is changed in the source.

`explicit_monohydrate` describes the ingredient wording only. The historical
names `Creatine Mono` and `Creatine; Micronized` do not spell out monohydrate;
they remain identifiable rather than being treated as chemical confirmation.

Each export retains all matched declarations, including repeated DSLD IDs and
unresolved quantities. `source_rowid` identifies a row in this exact database,
not a stable identifier across reimports. No serving selection, daily-dose
calculation or product-level conclusion is made by this step. The database is
opened read-only, and the scripts use Python's standard library.

## Comparing recorded amounts per label

```sh
python scripts/creatine_labels.py data/supplements.db --summary
python scripts/creatine_labels.py data/supplements.db --summary --ignore-case
python scripts/creatine_labels.py data/supplements.db > results/creatine-label-amounts.csv
python -m unittest discover -s tests -v
```

The CSV includes all matched label IDs; the JSON summary includes only exact
`On Market` status in the snapshot, not independently verified current sales.
Amounts are converted before taking minima/maxima, never summed. Ties retain
every contributing source row ID for lookup in the matching export. A label
with both usable and unresolved declarations is marked `partial`; its bounds
describe only the usable subset. An entirely unresolved label has blank bounds,
not zero. `complete` means all matched quantities parsed, not that a label was
reviewed or its serving basis validated. See the
[selection check](../docs/creatine-amount-selection.md) for counts and limitations.

## Directions, images and compact results

The bounded review can be inspected without the full database:

```sh
python scripts/creatine_directions.py
python scripts/creatine_label_checks.py
```

To check selection and saved excerpts against the original import, then rebuild
all compact counts:

```sh
python scripts/creatine_directions.py --database data/supplements.db
python scripts/creatine_results.py data/supplements.db --output results/reproduced
```

Compare `amount-screens.csv`, `review-counts.json`, `snapshot.json` and
`source-files.csv` in that output with [the saved results](../data/creatine-review/).
The output directory must be new; an existing directory is never overwritten.
For another run, choose a different path with `--output`.
The results script opens the database read-only, checks integrity, checks review
excerpts against it and verifies its fingerprint is unchanged after analysis.
The database hash is specific to this rebuild; semantic agreement and per-file
CSV fingerprints matter too if a different SQLite version changes the file layout.

API and image evidence came from separately saved DSLD responses. If those exact
files are available under `data/dsld/live-labels/ID.json` and
`data/dsld/label-pdfs/ID.pdf`, verify them with:

```sh
python scripts/creatine_label_checks.py --source-dir data/dsld
```

This checks API extraction and API/PDF hashes, not the correctness of a visual
reading. URLs and fingerprints are in
[label-checks.jsonl](../data/creatine-review/label-checks.jsonl). Their original
retrieval timestamps are unknown. Later downloads may differ and cannot silently
replace these sources. Third-party PDFs are linked rather than committed.

Small source excerpts and review decisions are included with the repository.
The full original January archive is retained separately and is needed for
end-to-end reproduction. The public DSLD homepage does not guarantee access to
that exact old export. This limits independent reproduction if the archive is
unavailable, even though the review arithmetic can still be inspected offline.
