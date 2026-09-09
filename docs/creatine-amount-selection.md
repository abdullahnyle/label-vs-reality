# Creatine amount-selection check

Computed on 9 September 2026 from the supplied January CSV archive, rebuilt
with the supported importer. This calculation checks recorded amounts; it does
not validate source text, serving instructions or label images.

Rebuilt database SHA-256:
`0a4ad89d95a5041b1d08165c9313a09f56570d43b9afc6867e72365e8558f448`.
Inputs: 214,780 ProductOverview rows, 2,020,130 DietarySupplementFacts rows,
16 ImportManifest entries; integrity `ok`, zero orphaned facts. The database
hash was unchanged after read-only analysis.

Use the two `creatine_labels.py --summary` commands in the
[loading instructions](../scripts/load_data.md) to reproduce this table.

| On-market snapshot label IDs | Exact aliases | ASCII case-insensitive aliases |
| --- | ---: | ---: |
| Matched | 1,278 | 1,370 |
| At least one usable amount | 916 | 957 |
| No usable amount | 362 | 413 |
| Usable and unresolved declarations mixed | 2 | 2 |
| Minimum usable amount at least 3 g | 559 | 578 |
| Maximum usable amount at least 3 g | 648 | 668 |
| Minimum below 3 g, maximum at least 3 g | 89 | 90 |
| Nonblank Suggested Use | 1,196 | 1,285 |

Using usable-label denominators, the exact-alias screen changes from 61.0%
with minima to 70.7% with maxima; the case-insensitive screen changes from
60.4% to 69.8%. Missing amounts are not classified as below 3 g. The two partial
labels are included in usable-label denominators, but their unresolved rows
remain visible in the CSV.

These are extrema of recorded ingredient declarations, not a claim that every
repetition represents a validated alternative serving. Values are converted to
grams before comparison; repeated entries are not added together. Extremum
source row IDs, including ties, connect each label summary to the raw matching
export from the same database. Neither extrema nor row IDs establish daily use,
chemical identity, actual composition, safety or efficacy. Three grams is a
descriptive screen retained for comparison with the earlier analysis, not a
newly validated clinical decision threshold.

Suggested Use coverage counts only nonblank database text. It does not establish
that daily directions are interpretable. A bounded, traceable directions review
and targeted image inspection remain the next evidence dependency; no broad
label audit or daily-dose conclusion follows from this table.

The January inputs are supplied research files, not committed to this repository.
Keep ProductOverview_1.csv through _8 and DietarySupplementFacts_1.csv through
_8 together with their acquisition ReadMe. ImportManifest records individual
file hashes. A new download from the NIH DSLD website is not a substitute for
that historical archive and need not reproduce these counts.
