# Seven checks against saved label images

These checks revisit seven previously saved, single-page DSLD PDFs on
10 September 2026 (Pakistan time). Five belong to the
[44-record directions review](creatine-directions.md). Two additional IDs,
551 and 209975, examine a serving-metadata conflict and multiple serving options.
The selection is purposeful and informed by earlier exploration; it cannot
estimate an error rate in DSLD or validate the remaining records.

The files in [label-checks.jsonl](../data/creatine-review/label-checks.jsonl)
retain the relevant CSV and API excerpts, API/PDF fingerprints, page locations
and the fresh image readings. The exact original retrieval timestamps were not
preserved, so `retrieved_on` is null. These are saved responses and images,
not a claim that the entire live database was checked on the review date.

| DSLD ID | Image observation | Consequence |
| --- | --- | --- |
| [57461](https://api.ods.od.nih.gov/dsld/s3/pdf/57461.pdf) | 2.5 g per two capsules; two at each of three named meals | Written schedule implies 7.5 g/day |
| [253763](https://api.ods.od.nih.gov/dsld/s3/pdf/253763.pdf) | 2800 mg per four capsules; four daily | Written default is 2.8 g/day, not 11.2 g |
| [328409](https://api.ods.od.nih.gov/dsld/s3/pdf/328409.pdf) | 1000 mg per two capsules; two twice daily | Written default is 2 g/day |
| [64731](https://api.ods.od.nih.gov/dsld/s3/pdf/64731.pdf) | 2250 mg per three capsules; maintenance three to five daily | Maintenance range is 2.25-3.75 g/day |
| [551](https://api.ods.od.nih.gov/dsld/s3/pdf/551.pdf) | 4200 mg per six capsules; six daily | Image supports 4.2 g/day; ingredient-row serving metadata says one capsule |
| [337727](https://api.ods.od.nih.gov/dsld/s3/pdf/337727.pdf) | Printed 6.400 mg and 3.200 mg occur in a daily-serving table | Punctuation and serving basis conflict with CSV/API; no corrected daily estimate |
| [209975](https://api.ods.od.nih.gov/dsld/s3/pdf/209975.pdf) | One, half and one-third scoops list 5000, 2500 and 1667.67 mg | Serving options cross 3 g; the daily ceiling is not a daily recommendation |

For 337727, German punctuation suggests a thousands-separator problem, but the
table also distinguishes daily servings and a Swiss instruction. Replacing the
decimal alone would not resolve the serving mapping. Its raw values stay in the
automated screen and it stays unresolved in the directions review.

For 551, top-level overview/API serving data agree with the six-capsule image;
the ingredient-row CSV/API serving quantity is one. Agreement between the CSV
and API on the 4200 mg amount therefore does not validate either serving basis.
The image-derived 4.2 g reading is supplementary, outside the 44-record totals.

The API comparison checks multisets of matched ingredient names and gram amounts,
retaining duplicates. It agrees for all seven IDs. That is consistency between
two representations from the same database, not independent chemical validation.
The image readings are manual interpretations and are not established by tests.

```sh
python scripts/creatine_label_checks.py
# If the original saved sources are available locally:
python scripts/creatine_label_checks.py --source-dir data/dsld
```

The second command verifies the saved API/PDF fingerprints and API extraction.
A later response at the same URL may differ; do not replace an old file and call
it the reviewed source. PDFs remain external third-party material. Neither
the scans nor the database measure physical product contents or actual intake.
