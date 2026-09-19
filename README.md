# Label vs. Reality

This project looks at the amounts of creatine recorded on supplement labels
and how serving sizes and directions change their interpretation.

The starting question was whether those amounts reached a daily reference of
3 grams. But a label might list the amount in two capsules and tell someone to
take those capsules three times a day. Comparing the first number with a daily
reference misses part of the story.

The analysis uses Python and SQLite with a January 2026 download from the NIH
[Dietary Supplement Label Database](https://dsld.od.nih.gov). The full download
contains 214,780 label records and just over 2 million ingredient records.
The study focuses on creatine, with a closer review of the directions for 44 labels
and seven saved label images.

## What changed when the labels were read more closely

Some labels have more than one recorded creatine amount. The first comparison
checks how much the result changes depending on which amount is selected.

Using the original list of ingredient names, there are 1,278 matching label IDs
marked `On Market` in the download. Of these, 916 have at least one usable amount.

| Amount selected for each label | Labels reaching 3 g |
| --- | ---: |
| Smallest recorded amount | 559 of 916 (61.0%) |
| Largest recorded amount | 648 of 916 (70.7%) |

That is a difference of 9.7 percentage points from one analytical choice. The
other 362 labels have no usable amount. They are kept separate rather than
counted as below 3 g. Allowing capitalization differences in ingredient names
also changes the selection. Using the largest amount then gives 69.8% among
957 labels with usable amounts.

The next step was to examine directions for 44 labels whose names contain
the word creatine and whose largest recorded amount is below 3 g, using the same
original ingredient list and market status. Their written schedules give:

- 17 of 44 reached at least 3 g per day under their written directions.
- 11 entirely below 3 g.
- Three with a range that crosses 3 g.
- 13 where the directions or serving information do not support a calculation.

One useful example is a label listing 2.5 g per two capsules with directions
to take two capsules at each of three meals. That adds up to 7.5 g over the
written day. Another lists 2.8 g per four capsules and directs four capsules
daily, so its daily amount stays at 2.8 g.

The label-image checks also showed that agreement inside the database was not
always enough. For selected records, I compared the CSV data, DSLD API response
and original label image directly. Some serving-information conflicts could not
be resolved safely from the database fields alone.

The clearest unresolved example is DSLD ID 337727. Its CSV/API quantities and
serving information do not map cleanly onto the values printed in the label's
daily-serving table. I kept the original record unchanged, documented the
conflict, and reported it to NIH/ODS for clarification on 19 September 2026
rather than treating it as a confirmed database error.

The [case study](docs/creatine-case-study.md) explains the comparisons and
examples in detail. The [results tables](data/creatine-review/amount-screens.csv)
include the other matching rules, market statuses and a 2.5 g comparison.

## What is in the repository

The Python code imports the 16 original CSV files into SQLite, keeps their text
intact and checks that ingredient records belong to valid label IDs. It converts
grams and milligrams before comparing amounts, keeps missing values separate,
and avoids counting repeated declarations as extra labels.

The [review records](data/creatine-review/) contain source excerpts, serving
calculations and the reasons for each decision. File and excerpt fingerprints
make it possible to check whether the underlying evidence has changed. The
[claim ledger](docs/claim-ledger.md) links the findings to that evidence and
explains which earlier interpretations were withdrawn.

The earlier [SQL reference and count queries](sql/README.md) are also included.
The magnesium files are earlier exploratory work outside this creatine study.

## Try it locally

You need Git and Python 3.11 or newer. There are no Python packages to install.

```sh
git clone https://github.com/abdullahnyle/label-vs-reality.git
cd label-vs-reality
python -m unittest discover -s tests -v
python scripts/creatine_directions.py
python scripts/creatine_label_checks.py
```

These commands run the tests and check the saved review evidence without the
full database. A [GitHub workflow](.github/workflows/checks.yml) is configured
to run the same checks on Linux and Windows with Python 3.11 and 3.13.

To rebuild the full analysis, follow the [loading instructions](scripts/load_data.md).
You will need the original January CSV files, which are not bundled in Git.
Their [fingerprints](data/creatine-review/source-files.csv) identify the exact
inputs. A new NIH download may have different records, so it may produce
different counts.

## What these results can tell us

The main finding is about how choices in handling label data affect a conclusion.
The 3 g reference helps compare recorded amounts. It cannot establish whether
a supplement works. The project does not measure the contents of a bottle,
what someone actually consumes or a product's safety.

The 44 labels and seven images were selected for closer inspection, so their
results should not be used to estimate rates across the whole market. Labels
can also represent related versions of a product, and `On Market` refers to
January 2026. The manual interpretations have not been checked by a second
reviewer.

Code and project documentation use the [MIT licence](LICENSE). Third-party label
material retains its original rights. The saved PDFs are not included.
