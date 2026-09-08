# Source review record

Reviewed on 8 September 2026 with ChatGPT assistance. Abdullah has not yet
independently reviewed these decisions. The inputs are the original January CSV
snapshot and separately retrieved current DSLD API responses and scanned labels.

## Scope

| Evidence | Coverage | What was checked |
|---|---:|---|
| Candidate source text | 44 IDs | Recorded form, serving basis and Suggested Use; bounded daily interpretations where justified |
| Suggested Use sample | 30 IDs | Fixed schedule, ranges, phases, workout conditions and missing frequency |
| Live DSLD API | 58 IDs | Matched ingredient amount multisets and preserved parent/serving context |
| Scanned label PDFs | 7 IDs | Printed quantities, serving basis and relevant instructions |

The API sample comprises all 44 candidates plus 14 purposeful checks. Six are
the first two textual IDs among unnamed on-market records in each amount category
(10960, 12707; 12854, 14625; 12766, 1312). Four cover every partly unresolved label
(21437, 22022, 211083, 211460). Three revisit multiple-row examples from the old
investigation (182876, 209975, 268422). ID 551 checks a capsule serving. This is
purposeful coverage, not a random error-rate sample.

All 58 API comparisons agree on matched amounts after the documented CSV/API
representation mapping. This does not validate the API against the manufacturer
image. Missing CSV quantities correspond to NP placeholders in selected API
records; those placeholders were not treated as zero intake. Parent-blend rows
remain context and are never substituted for a missing ingredient amount.

The image sample was chosen to inspect the extreme value at 337727, compare facts
and overview serving metadata at 551, check daily schedules at 57461, 253763,
328409 and 64731, and confirm multiple serving options at 209975. All were
single-page PDFs. `image-checks.csv` records URLs, hashes, locations and decisions.
The PDFs are linked, not republished under the project's license.

## Files and reproduction

`candidate-decisions.csv` and `suggested-use-decisions.csv` contain the individually
recorded decisions. The exported reviews join these decisions to source text,
IDs and selected row numbers. No automated output is marked as a human review.

```sh
python scripts/review_labels.py results/local-run data/dsld/live-labels results/local-review --reviewed-on 2026-09-08
```

The API input folder contains one JSON response per ID, obtained from
`https://api.ods.od.nih.gov/dsld/v9/label/{id}`. Published API checks give the exact
IDs and response hashes. Re-fetching later can return changed source data; do not
substitute a later response and claim it is the one reviewed here. Compact
excerpts of the reviewed responses are published in `review/api_context.jsonl`.

The published candidate daily estimates use:

`recorded grams / units per recorded serving * stated daily units`

Units may be capsules or whole servings, as specified by each decision. These
estimates describe only the explicit schedule and phase. Ranges stay ranges;
loading, training days and physician alternatives are not silently generalized.
No daily estimate is given for disputed record 337727. Source-text review does
not establish clinical adequacy, actual contents or compliance with directions.

The 30-record sample uses seed 20260907 and textual ID ordering. Its classifications
are a new review, not a reconstruction of the old unseeded sample. The classifications
show variation; they do not establish that automated extraction is impossible.

`ingredient-coverage.csv` records every unmatched name containing the text pattern
creatin...monohydrat in this snapshot. Only case variants enter the additional
comparison. It is a focused coverage check, not a complete ingredient ontology.
