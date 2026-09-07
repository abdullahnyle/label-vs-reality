# Label vs. Reality

An exploratory study of recorded creatine amounts in NIH's Dietary Supplement
Label Database (DSLD). The question is how label amounts vary, how much data is
usable, and how the answer changes when a label lists several serving options.

The analysis uses SQLite for matching and aggregation, with a small Python
standard-library layer for CSV loading, quantity validation and reproducible
exports. The unit of analysis is a **distinct DSLD label ID**, not necessarily a
unique physical product.

## Current status

The pipeline has been rebuilt and checked against synthetic fixtures. The original
DSLD snapshot is not included in the repository and has not yet been rerun through
this version. **There is no validated dataset result for this version yet.**

Earlier local work reported 1,278 ingredient-matched IDs marked on-market: 648 at
least 3 g per serving, 268 below 3 g and 362 with no usable amount. That gives 70.7%
among 916 usable records, with 28.3% of the full cohort unassessable. These are
historical observations awaiting reconciliation, not outputs of the current code.
The [claim ledger](docs/claim-ledger.md) records their status.

Two errors in the earlier SQL motivated the rebuild:

- Later statements tried to reuse CTEs after their statement had ended.
- Raw amounts were ranked before unit conversion, so 500 mg could be selected
  instead of 4 g. Blank or malformed text could also become zero in arithmetic.

The new analysis validates amounts first, preserves unresolved values, and reports
both maximum and minimum usable amounts. It exports source fields and review
queues so that automated results can be checked against the labels.

## Run it

Python 3.10 or newer with SQLite 3.25 or newer is sufficient; no third-party Python
packages are required. Start in the repository root.

```sh
python scripts/load_data.py data/dsld/extracted data/supplements.db
python scripts/analyze.py data/supplements.db results/local-run --dataset-label "DSLD original snapshot"
python -m unittest discover -s tests -v
```

An existing database with the required DSLD tables can be passed directly to
`analyze.py`. The analysis opens it read-only. Close the database editor and save
pending work first. Both commands refuse to replace existing outputs.

The [loading instructions](scripts/load_data.md) explain provenance, schema
requirements and what to do when the original download date is unknown.

A run produces a report and figure, record and source-row exports, parsing counts,
threshold/serving/market sensitivity comparisons, a candidate review queue, a
repeatable Suggested Use sample and a provenance manifest. Generated queues are
**pending reviews**, not completed classifications.

## What the analysis measures

The primary screen uses the largest usable recorded amount for each label ID and
compares it with 3 g. The alias list includes the original 25 ingredient strings;
a separate comparison excludes two names that do not explicitly say monohydrate.
Ingredient wording alone does not verify chemical identity.

The 3 g screen is motivated by the low end of the typical 3–5 g/day maintenance
range discussed in the [2017 ISSN position stand](https://doi.org/10.1186/s12970-017-0173-z).
A per-serving amount does not establish daily intake or effectiveness. At least
3 g also includes amounts above 5 g; it does not mean within the reference range.

Names containing “creatine” identify a group for review. Names without that word
are not automatically irrelevant products. Blends remain part of the broad
ingredient-matched cohort.

See [methodology](docs/methodology.md) for the selection rules and limitations,
and [discussion notes](docs/defending-the-analysis.md) for the reasoning behind them.

## Data and limits

[NIH DSLD](https://ods.od.nih.gov/Research/Dietary_Supplement_Label_Database.aspx)
contains recorded label information, including historical entries. Market status
is taken from the snapshot and is not a check of current retail availability.
This is not a representative market survey or a laboratory assay. Absorption,
actual contents, price, clinical outcomes and manufacturer intent are not measured.
Full daily-dose extraction is outside this version's scope.

The historical database reportedly contained 214,780 ProductOverview rows. A new
download may have a different size; it must be treated as a separate snapshot.
DSLD identifies its data as public domain under CC0 in its
[API guide](https://dsld.od.nih.gov/api-guide). Large raw files are excluded for
size, and source provenance is retained separately from the project's MIT license.

The earlier magnesium work is exploratory. Its chemical reference is not applied
to label amounts, and the repeated rows for ID 239649 remain unresolved.

## License

Project code and documentation: [MIT](LICENSE). Source data: NIH DSLD, CC0.
