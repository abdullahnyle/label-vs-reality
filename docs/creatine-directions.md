# Reading the directions after the amount screen

The review selects every January-snapshot label with exact `On Market` status,
`creatine` anywhere in its product name (case-insensitive), and a usable maximum
amount below 3 g under the historical 25-name ingredient rule. This gives 44
label IDs. Selection is reproduced by `candidate_ids` in
[creatine_directions.py](../scripts/creatine_directions.py).

This is a targeted set of low recorded amounts, not a random sample or a count
of unique commercial products. Similar names and instructions remain separate
label records. The name filter neither proves a dedicated creatine product nor
excludes other active ingredients. No results from a different 30-record sample
are incorporated into this review.

## Review rules

Read the recorded Suggested Use together with the overview and ingredient-row
serving descriptions. A daily calculation needs an explicit amount, a supported
serving-to-unit mapping, and a daily frequency or named schedule. The CSV stores
the chosen units and a reason for each decision; code checks the arithmetic,
not the correctness of the reading.

- Keep ordinary daily, maintenance and normal-training schedules distinguishable.
- Do not pool loading with maintenance or normal with intensive training.
- Use a stated default while noting unspecified practitioner alternatives.
- Do not turn workout timing, a maximum allowance or a self-selected goal into
  a universal daily schedule.
- Keep absent directions, missing frequency, uncertain serving mappings and
  source conflicts unresolved. An unresolved result is not zero.
- Use the matched monohydrate declaration only. Do not add other creatine forms
  or a parent blend, or convert monohydrate mass to anhydrous creatine mass.

For supported readings:

`daily grams = recorded ingredient grams / units per serving * stated daily units`

The 3 g comparison remains descriptive. These calculations are interpretations
of written schedules, not measured consumption or evidence of effectiveness.

## Evidence and reproduction

Reviewed from the source text on 10 September 2026 (Pakistan time).
[directions-source.jsonl](../data/creatine-review/directions-source.jsonl) retains
the relevant CSV text, all creatine-related rows and source row IDs.
[directions.csv](../data/creatine-review/directions.csv) contains 44 decisions,
including the unresolved ones. Each decision is tied to a SHA-256 of its source
excerpt; changed text invalidates the calculation rather than reusing a stale
interpretation. Row IDs identify this import, not a universal DSLD row number.

The source was rebuilt from the 16 supplied CSV batches, acquired
2026-01-10T17:52:06-05:00 according to their ReadMe. Rebuilt database SHA-256:
`0a4ad89d95a5041b1d08165c9313a09f56570d43b9afc6867e72365e8558f448`.

```sh
# Check arithmetic and source bindings using the committed excerpts:
python scripts/creatine_directions.py
# Also reconstruct the selection and compare every excerpt with the original import:
python scripts/creatine_directions.py --database data/supplements.db
```

The first command does not establish that the excerpts were faithfully extracted;
the second checks that relationship against the database. Neither is an independent
review of the classifications. Selected scans provide a separate check of the
underlying printed text; the other records remain source-text interpretations.
