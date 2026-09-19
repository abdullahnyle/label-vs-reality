# Claim ledger

The supported calculations use the Python workflow in
[the reproduction instructions](../scripts/load_data.md). Older SQL notes are
historical exploration; the statements below supersede their interpretation.

| Statement | Evidence | Boundary |
| --- | --- | --- |
| The rebuilt input contains 214,780 overview and 2,020,130 facts rows from 16 files | [Snapshot](../data/creatine-review/snapshot.json), [manifest](../data/creatine-review/source-files.csv) | This January archive, not the present live database |
| Exact on-market matching gives 1,278 IDs: 916 usable and 362 unresolved | [Amount screens](../data/creatine-review/amount-screens.csv), [selection note](creatine-amount-selection.md) | Two usable labels contain unresolved declarations too |
| Exact-match maxima reach 3 g for 648/916 (70.7%); minima for 559/916 (61.0%) | Same amount screens; `creatine_labels.py --summary` | Recorded extrema, not typical servings or daily intake |
| ASCII case-insensitive maxima reach 3 g for 668/957 (69.8%) | Same amount screens, separate matching row | A sensitivity analysis of the reviewed aliases, not exhaustive ingredient discovery |
| Forty-four selected low-maximum labels yield 17 at/above, 11 below, three crossing and 13 unresolved daily interpretations | [Decisions](../data/creatine-review/directions.csv), [counts](../data/creatine-review/review-counts.json), [rules](creatine-directions.md) | Targeted records; loading and intensive-training alternatives are not pooled |
| CSV/API matched amounts agree for seven inspected IDs | [Source checks](../data/creatine-review/label-checks.jsonl) | Same-source consistency; serving metadata can still conflict |
| Image checks support the stated examples and identify conflicts at 551 and 337727 | [Image readings](creatine-label-checks.md) | Seven purposeful checks, no population error-rate estimate |

## Interpretations withdrawn

- Reaching 3 g per recorded serving does not establish effectiveness. Falling
  below it does not establish ineffective or deceptive labelling.
- Product names do not establish manufacturer intent or distinguish all dedicated
  creatine products from blends. The earlier contamination interpretation is withdrawn.
- The earlier 26/18 and 25/16/2/1 product-format splits are not findings of this
  fresh review; classification of format is not needed for its daily calculations.
- The earlier 30-directions and 58-API samples are not included in the new review
  totals. Only the evidence explicitly reproduced here supports these statements.
- The cited ISSN paper does not support the earlier additional body-size commentary.
  Its maintenance range is described with its conditions in the [case study](creatine-case-study.md).

## Still unresolved

Thirteen of the 44 reviewed labels do not support a reliable daily calculation
under these rules.

ID 337727 is the clearest source-level discrepancy found during the label checks.
The CSV/API quantities and serving information do not map cleanly onto the
printed daily-serving table. The punctuation may reflect a European thousands
separator, but changing that interpretation alone does not resolve the serving
basis.

Because there is not enough evidence to justify a correction, the original
database values remain unchanged in the analysis and no corrected daily amount
is claimed. I reported the record to NIH/ODS for clarification on
19 September 2026. It remains unresolved unless the source is clarified or
updated.

ID 306204 also remains unresolved because the reviewed source does not provide
enough information to map the scoop quantity reliably.

These unresolved cases stay in the result rather than being forced into the
above/below-3 g groups. No claim is made about unreviewed images, independent
coding agreement, complete ingredient coverage, real contents or measured intake.
