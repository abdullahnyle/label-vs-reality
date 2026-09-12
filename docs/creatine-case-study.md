# What changed when the creatine labels were read more closely?

A low amount in a database field is not enough to conclude that a supplement's
daily instructions supply a low amount. This case study follows that distinction
through a January 2026 DSLD snapshot: first an ingredient-amount screen, then a
targeted directions review, then selected checks against label images.

## The question and the sample

The broad question is how the fraction of recorded label amounts reaching 3 g
changes with ingredient matching and minimum/maximum selection. The unit is a
DSLD label ID, not a unique current commercial product or a consumer's intake.

The supplied archive contains 214,780 overview records and 2,020,130 facts rows.
Its ReadMe records acquisition on 10 January 2026. The current importer preserves
text, fingerprints each CSV batch and checks the relationship between tables.
[Snapshot checks](../data/creatine-review/snapshot.json) and the
[16-file manifest](../data/creatine-review/source-files.csv) identify the input.

The [NIH description of DSLD](https://ods.od.nih.gov/Research/Dietary_Supplement_Label_Database.aspx)
explains that it includes on- and off-market labels and is updated for label and
formulation changes. `On Market` here means that status in this snapshot. This
is not a census of products currently for sale or a representative sales sample.

The historical 25-name match list is retained to make the earlier analysis
comparable. ASCII case-insensitive matching is shown separately. Two historical
aliases do not spell out monohydrate; naming is not proof of chemical identity.
The list is not a complete ontology of creatine ingredients.

## Why the 3 g screen needs care

The [2017 ISSN position stand](https://link.springer.com/article/10.1186/s12970-017-0173-z),
in its supplementation-protocols section, describes 3-5 g/day as a general
maintenance intake after saturation, with some larger athletes potentially
needing 5-10 g/day. That is a daily reference, not a universal per-serving
effectiveness cutoff. It does not justify the earlier body-size claims in the
exploratory reference notes. This study uses 3 g as a descriptive screen and
2.5 g only as a sensitivity check, not a revised clinical recommendation.

## Recorded amounts depend on the selection rule

| On-market matching rule | Matched IDs | Usable | Unresolved | Minimum reaches 3 g | Maximum reaches 3 g |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical exact names | 1,278 | 916 | 362 | 559 / 916 (61.0%) | 648 / 916 (70.7%) |
| ASCII case-insensitive names | 1,370 | 957 | 413 | 578 / 957 (60.4%) | 668 / 957 (69.8%) |

For exact matching, 89 usable labels cross 3 g between their recorded minimum
and maximum. Missing quantities are not assigned to the below-3 g group. Two
labels in each on-market screen have both usable and unresolved declarations;
their bounds cover only the usable subset. Repeated quantities are not summed.

At 2.5 g, the exact on-market screen gives 666 / 916 (72.7%) using minima and
694 / 916 (75.8%) using maxima. Including off-market labels at 3 g gives
925 / 1,576 (58.7%) and 1,038 / 1,576 (65.9%). These are different descriptive
questions. None should be selected merely because it produces a stronger claim.
All matching, population and threshold combinations are in
[amount-screens.csv](../data/creatine-review/amount-screens.csv).

## Directions change some interpretations and leave others open

The [directions review](creatine-directions.md) selects 44 exact-match on-market
IDs with `creatine` in the name and a maximum recorded amount below 3 g.
Reviewing the source text yields:

| Interpretation of the selected written schedule | Label IDs |
| --- | ---: |
| Entire daily range at or above 3 g | 17 |
| Entire daily range below 3 g | 11 |
| Daily range crosses 3 g | 3 |
| No supported daily calculation | 13 |

The 31 calculations include 26 ordinary daily defaults, three maintenance
schedules and two normal-training schedules. They do not combine loading or
intensive-training instructions with those defaults. No market-wide daily-dose
percentage follows from this selected set. The eleven below-screen readings
also do not establish ineffectiveness, mislabelling or manufacturer intent.

Examples show why the distinction matters. ID 57461 records 2.5 g per two
capsules, with two capsules at each of three named meals: 7.5 g over that written
day. ID 253763 records 2.8 g per four capsules and directs four daily: 2.8 g,
not 11.2 g. ID 64731 specifies a maintenance range of 2.25-3.75 g/day.

## Database agreement is not image validation

[Seven saved image checks](creatine-label-checks.md) cover five of the candidates
and two supplementary examples. CSV/API ingredient amounts agree for all seven,
yet ID 551 has a serving-metadata conflict and ID 337727 has unresolved
punctuation and daily-serving differences. ID 209975 confirms several serving
options whose recorded amounts lie on both sides of 3 g.

The raw screen is not retrospectively corrected from these examples. Image
readings remain separately recorded; 337727 has no asserted corrected daily
quantity. This is a purposeful sample, not an estimated database error rate.

## What this study establishes

The initial low-amount interpretation depended on choices about population,
units, repeated records and daily use. Recomputing the screen and reading the
directions narrowed that interpretation instead of preserving the original claim.
The result is evidence about label-data structure and analytical sensitivity.

The review is not blinded or independently double-coded. Saved API responses
are another representation of DSLD, not an independent assay. Product versions
and similar labels may be correlated. Original input files are needed for full
reproduction; a fresh download can differ. The work does not establish actual
contents, safety, efficacy, legal compliance or what anyone consumed.

After [importing the original snapshot](../scripts/load_data.md), regenerate the
compact counts with:

```sh
python scripts/creatine_results.py data/supplements.db --output results/reproduced
```

Choose a new output directory for each run to preserve previous results.
The committed excerpts also permit inspection of each directions decision
without downloading the entire snapshot.
