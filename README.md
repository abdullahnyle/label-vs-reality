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
have a recorded per-serving amount of at least 3g, the low end of the
ISSN's 3-5g/day maintenance-dose range (Kreider et al. 2017).**

That's a threshold description, not a claim that these products are
"effective" — this project doesn't measure absorption, adherence, or real-
world outcomes, only what's printed on the label relative to a published
reference range. A product at 3g/serving matches the ISSN's low end; the
range itself runs to 5g, and this figure doesn't distinguish 3g from 8g,
only "at least 3g" from "under 3g."

That number came out of fixing two real methodology problems, not from a
clean first pass.

**Off-market labels were skewing the result.** DSLD includes historical and
discontinued labels alongside current ones. The first pass at this analysis
didn't filter for that. Off-market products turned out to be 41% of the raw
ingredient match, and restricting to on-market-only moved the share hitting
the 3g threshold from an initial ~66% to the ~71% figure above.

**Most of what looked like low-dose creatine wasn't a real creatine product
at all.** Filtering to products whose ingredient list matches "creatine
monohydrate" exactly, mass gainers and whey blends that include a small
amount of creatine as one ingredient among many show up in the same filter.
Of the products landing under 3g, about 84% aren't even named as creatine
products — they're contamination from other categories, not evidence that
dedicated creatine products fall short of the threshold.

## What this doesn't establish

This is a per-serving amount analysis, not a daily-dose analysis. Those are
different questions. A capsule product listing 700mg per capsule isn't
necessarily underdosed if the label recommends four capsules a day — that
would be 2.8g, close to the reference range.

I looked into whether a daily-dose version of this analysis was possible.
`Suggested Use` — the field that would give the real daily total — is
populated for 93.6% of on-market products, so coverage isn't the blocker.
The content is. A random sample of that field turned up single doses
("take 2500mg daily"), dose ranges that vary by training day or bodyweight,
separate loading and maintenance phases with different amounts each, and
free text with no dosing information at all on products where creatine is
a minor ingredient in a larger formula. There's no consistent structure to
extract a single daily-gram figure from automatically without either
building a parser whose coverage would be biased toward whichever text
patterns it happens to catch, or reading every entry by hand.

I chose not to do either for this pass. A daily-dose figure built on biased
automated parsing would look more rigorous than the per-serving figure
above while actually being less trustworthy, and that's a worse outcome
than stating the limitation plainly. Per-serving amount is what this
analysis measures, and the reason it's not a daily-dose analysis is a
finding in itself, not an oversight.

## Still open

- One duplicate DSLD record (magnesium glycinate, ID 239649) with no
  discoverable cause — flagged rather than quietly dropped.

See `docs/claim-ledger.md` for the full source and confidence breakdown
behind every claim above.

## Approach

DSLD product and ingredient data loaded into SQLite across two tables:
`ProductOverview` (product identity, market status, serving size) and
`DietarySupplementFacts` (per-ingredient dose data), joined on DSLD ID.
Reference doses come from a hand-built table (`CreatineFormReference`,
`MagnesiumFormReference`) sourced from peer-reviewed and authoritative
references, not manufacturer claims.

## Data

Source: [DSLD](https://dsld.od.nih.gov). DSLD's own API is published under a
[CC0 1.0 public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/),
so redistribution isn't the issue — raw files aren't included here because
of size, not licensing. See `scripts/load_data.md` to rebuild the database
yourself.

## License

MIT. See `LICENSE`.
