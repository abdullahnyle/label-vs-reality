# Claim Ledger

This tracks the claims in this project that are solid enough to publish, versus the ones that are still open. Nothing here gets called VERIFIED just because it's been said a few times — it's VERIFIED only if it's been directly checked against the data.

---

## The sample

Creatine analysis runs on `DietarySupplementFacts` joined to `ProductOverview` by DSLD ID, filtered to an exact list of 25 creatine monohydrate ingredient-name variants, on-market products only.

`ProductOverview` has 214,780 rows and 214,780 distinct DSLD IDs — no duplicates at that level. Four tables total in the database: `ProductOverview`, `DietarySupplementFacts`, and two hand-built reference tables, `CreatineFormReference` and `MagnesiumFormReference`.

One thing worth flagging: a single physical product can have more than one DSLD ID if it's listed at multiple serving sizes. That's real and it's been checked, not a bug.

**Status: verified.**

---

## Market status mattered more than expected

DSLD keeps historical and discontinued labels alongside current ones. The first pass at this analysis didn't filter for that.

Turns out 41% of the raw creatine match (885 of 2,163 products) is off-market. Restricting to on-market-only moved the effective-dose rate from about 66% to about 71%. That's a real shift, not a rounding difference, and it's the reason the number below supersedes the earlier one.

**Status: verified.**

---

## The headline number

**About 71% of on-market creatine products with usable dose data hit the 3-5g/day reference range** (ISSN position stand, Kreider et al. 2017), measured as amount per serving.

Exact figures: 1,278 on-market products. 648 hit ≥3g, 268 land under it, 362 have no usable dose data. 648 out of the 916 with real numbers is 70.7%.

Unit parsing was checked against the actual unit strings in the data (`Gram(s)`, `mg`, `g`) — nothing fell through uncounted.

**Status: verified. Replaces the earlier ~66% figure, which mixed on- and off-market products. Don't use the old number anywhere going forward.**

---

## This measures per-serving amount, not daily dose

That's a real limitation, not a footnote. A capsule product might say 700mg per capsule and still add up to an effective dose if you're meant to take four a day — but that requires the label's `Suggested Use` field, and for the capsule products in the under-3g group, that field is empty. All 26 of them.

So for those 26, whether they actually reach an effective daily dose can't be answered from this data. Not "probably fine," not "probably underdosed" — genuinely unknown, and that's worth saying plainly rather than picking whichever guess sounds better.

**Status: verified that the field is blank. Open on what the real dosing looks like.**

---

## Most of the "underdosed" signal isn't creatine underdosing

Of the 268 on-market products under 3g, 224 of them (84%) aren't even named as creatine products. They're mass gainers, whey blends, and similar — creatine's just one ingredient among many, and it was never the point of the product. That's contamination from the ingredient-text match, not evidence that real creatine products are underdosed.

Only 44 products are both named creatine and genuinely under 3g. Of those, 18 look like real, single-serving low-dose products — several cluster right around 2.5g, which matches a pattern already noticed earlier in the project (a handful of brands seem to intentionally dose just under the 3g line). The other 26 are the capsule group above, where the real answer is unknown rather than resolved either way.

**Status: verified on the counts. The 2.5g grouping is a reasonable read of the data, not independently confirmed — call it a pattern, not a fact.**

---

## Two loose ends, left open on purpose

**A magnesium glycinate product (DSLD ID 239649) lists the same ingredient twice**, identical in every column, with no explanation findable in the data. Checked twice, across two different database states, same result both times. This isn't a creatine finding, but it's the clearest example in this dataset of something that just doesn't have an answer, and it's worth keeping visible rather than quietly dropping it.

**The on-market and mixed-population named-under-3g rates don't quite match** — about 16% on-market versus about 12% mixed. Small gap, doesn't change the headline number, but nobody's dug into why yet.

**Status: open. Not blocking anything, just not pretending to be solved.**
