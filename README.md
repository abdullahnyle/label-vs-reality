# Label vs. Reality

I started this project with a simple question: how often do the creatine amounts
recorded on supplement labels reach a 3 gram daily reference?

It turned out to be less simple than that. A label can list one amount per serving
but tell someone to take that serving more than once a day. Some labels also have
more than one recorded creatine amount. So the answer depends on how the data is
read and what exactly is being compared.

I used Python and SQLite with a January 2026 download from the NIH
[Dietary Supplement Label Database](https://dsld.od.nih.gov). The full download
contains 214,780 label records and just over 2 million ingredient records. I used
creatine as the case study, then manually reviewed the written directions for
44 selected labels and checked seven saved label images.

## What changed when I looked more closely

Using the original list of creatine ingredient names, I found 1,278 matching
label IDs marked `On Market`. Of those, 916 had at least one usable recorded
amount.

| Amount selected for each label | Labels reaching 3 g |
| --- | ---: |
| Smallest recorded amount | 559 of 916 (61.0%) |
| Largest recorded amount | 648 of 916 (70.7%) |

That is a 9.7 percentage point difference caused by one analytical choice.

The remaining 362 labels did not have a usable amount, so I kept them separate
instead of counting them as below 3 g. I also checked how capitalization in
ingredient names affected the result. With case-insensitive matching and the
largest recorded amount, 69.8% of 957 usable labels reached 3 g.

The next step was to read the directions for 44 selected labels whose largest
recorded amount was below 3 g. Their written schedules gave a more complicated
picture:

- 17 reached at least 3 g per day under their written directions.
- 11 stayed below 3 g.
- Three had a range that crossed 3 g.
- 13 could not be calculated reliably from the available serving information.

For example, one label records 2.5 g per two capsules but tells the user to take
two capsules at each of three meals, which adds up to 7.5 g over the written day.
Another records 2.8 g per four capsules and directs four capsules daily, so its
daily amount stays at 2.8 g.

I also compared selected CSV records and DSLD API responses with the original
label images. That mattered because agreement inside the database did not always
mean the serving information lined up cleanly with the printed label.

The clearest unresolved case is DSLD ID 337727. Its CSV/API quantities and
serving information do not map cleanly onto the values printed in the label's
daily-serving table. I left the original record unchanged, documented the
conflict, and reported it to NIH/ODS for clarification on 19 September 2026
rather than treating it as a confirmed database error.

The [case study](docs/creatine-case-study.md) goes through the comparisons and
examples in more detail. The [results tables](data/creatine-review/amount-screens.csv)
include the other matching rules, market statuses and a 2.5 g comparison.

## What is in the repository

The Python workflow imports the 16 original CSV files into SQLite and keeps the
source text intact. It checks that ingredient records belong to valid label IDs,
converts grams and milligrams before comparison, keeps missing values separate,
and avoids counting repeated declarations as extra labels.

The [review records](data/creatine-review/) contain the source excerpts, serving
calculations and reasons behind each manual decision. File and excerpt
fingerprints make it possible to check whether the evidence has changed. The
[claim ledger](docs/claim-ledger.md) links the main findings back to that
evidence and records interpretations that were later withdrawn.

The earlier [SQL reference and count queries](sql/README.md) are also kept in the
repository. The magnesium files are earlier exploratory work and are separate
from the creatine study.

## Try it locally

You need Git and Python 3.11 or newer. There are no Python packages to install.

```sh
git clone https://github.com/abdullahnyle/label-vs-reality.git
cd label-vs-reality
python -m unittest discover -s tests -v
python scripts/creatine_directions.py
python scripts/creatine_label_checks.py
```

These commands run the tests and check the saved review evidence without needing
the full database. A [GitHub workflow](.github/workflows/checks.yml) runs the
same checks on Linux and Windows with Python 3.11 and 3.13.

To rebuild the full analysis, follow the [loading instructions](scripts/load_data.md).
You will need the original January CSV files, which are not included in Git.
Their [fingerprints](data/creatine-review/source-files.csv) identify the exact
inputs used here. A newer NIH download may contain different records, so the
counts may also change.

## What the results do and do not show

The main result is not that one percentage is the "correct" answer. It is that
reasonable choices about how label data is handled can materially change the
conclusion.

The 3 g reference is useful for comparing recorded amounts, but it does not show
whether a supplement works, what is actually inside a bottle, what someone
really consumes, or whether a product is safe.

The 44 direction reviews and seven image checks were selected for closer
inspection, so they should not be used to estimate rates across the whole market.
A DSLD label record is also not automatically the same thing as a unique physical
product, and `On Market` refers to the January 2026 snapshot. The manual
interpretations have not yet been checked by a second reviewer.

Code and project documentation use the [MIT licence](LICENSE). Third-party label
material keeps its original rights. The saved PDFs are not included.
