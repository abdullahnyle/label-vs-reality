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
