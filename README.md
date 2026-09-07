# Label vs. Reality

Where's the gap between what a supplement's label claims and what's actually
worth taking? Which forms, doses, and products are underdosed, poorly
absorbed, overpriced, or don't even contain what they say?

Real product labels from NIH's Dietary Supplement Label Database (DSLD),
214,780 labels, joined against a hand-built reference table of what actually
works.

---

## Creatine — first finding

**About 71% of on-market creatine monohydrate products with usable dose data
deliver an effective dose (≥3g per serving), based on the ISSN's 3-5g/day
maintenance-dose reference (Kreider et al. 2017).**

That number came out of fixing two real methodology problems, not from a
clean first pass.

**Off-market labels were skewing the result.** DSLD includes historical and
discontinued labels alongside current ones. The first pass at this analysis
didn't filter for that. Off-market products turned out to be 41% of the raw
ingredient match, and restricting to on-market-only moved the effective-dose
rate from an initial ~66% to the ~71% figure above.

**Most of what looked like underdosing wasn't creatine underdosing at all.**
Filtering to products whose ingredient list matches "creatine monohydrate"
exactly, mass gainers and whey blends that include a small amount of
creatine as one ingredient among many show up in the same filter. Of the
products landing under 3g, about 84% aren't even named as creatine products
— they're contamination from other categories, not evidence that dedicated
creatine products are underdosed.

## What this doesn't establish

This is a per-serving amount analysis, not a daily-dose analysis. Those are
different questions. A capsule product listing 700mg per capsule isn't
necessarily underdosed if the label recommends four capsules a day — that
would be 2.8g, close to the reference range. Checking that requires the
`Suggested Use` field.

For the 26 capsule-format products in this dataset that land under 3g per
serving, `Suggested Use` is blank. Whether these products actually reach an
effective daily dose can't be determined from this data. That's a real limit
of what DSLD records, not a gap in this analysis — and it's the reason this
project measures per-serving amount rather than claiming to measure daily
dose.

## Still open

- One duplicate DSLD record (magnesium glycinate, ID 239649) with no
  discoverable cause — flagged rather than quietly dropped.
- A modest, unexplained gap between the on-market and mixed-population
  named-under-3g rates (16.4% vs 12.1%).
- Whether `Suggested Use` is usable for daily-dose analysis beyond the
  capsule subgroup checked here.

See `docs/claim-ledger.md` for the full reasoning and status behind every
claim above.

## Approach

DSLD product and ingredient data loaded into SQLite across two tables:
`ProductOverview` (product identity, market status, serving size) and
`DietarySupplementFacts` (per-ingredient dose data), joined on DSLD ID.
Reference doses come from a hand-built table (`CreatineFormReference`,
`MagnesiumFormReference`) sourced from peer-reviewed and authoritative
references, not manufacturer claims.

## Data

Source: [DSLD](https://dsld.od.nih.gov). Raw files aren't included here
(large, not mine to redistribute, easy to re-download). See
`scripts/load_data.md` to rebuild the database yourself.

## License

MIT. See `LICENSE`.
