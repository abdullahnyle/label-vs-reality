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

**About 71% of on-market creatine products with usable dose data have a recorded per-serving amount of at least 3g** — the low end of the ISSN's 3-5g/day maintenance-dose range (Kreider et al. 2017).

This is a threshold description, not an efficacy claim. It says the labeled amount meets or exceeds 3g; it doesn't say the product works, gets absorbed, or matches what a user actually takes daily. It also doesn't distinguish 3g from 8g — only "at least 3g" from "under 3g."

Exact figures: 1,278 on-market products. 648 hit ≥3g, 268 land under it, 362 have no usable dose data. 648 out of the 916 with real numbers is 70.7%.

Unit parsing was checked against the actual unit strings in the data (`Gram(s)`, `mg`, `g`) — nothing fell through uncounted.

**Status: verified. Replaces the earlier ~66% figure, which mixed on- and off-market products. Don't use the old number anywhere going forward.**

---

## This measures per-serving amount, not daily dose, on purpose

A capsule product might say 700mg per capsule and still add up to an effective dose if you're meant to take four a day. Checking that means reading `Suggested Use`, the field with the actual daily directions.

That field is populated for 93.6% of on-market products (1,196 of 1,278), so it's not a coverage problem. It's a structure problem. A random sample of 30 populated entries turned up plain single doses, dose ranges that depend on training day or bodyweight, separate loading and maintenance phases with different amounts, and — on products where creatine is a minor ingredient in a bigger formula — directions with no creatine dosing information at all. There's no consistent shape to pull a single daily-gram number out of automatically without the result being biased toward whatever pattern the parser happens to catch, and reading all ~1,196 entries by hand wasn't done for this pass.

Per-serving is what this analysis actually measures. Not being able to cleanly convert to daily dose is a real property of this dataset, not a step that got skipped.

**Status: verified (the coverage figure, and the structural variety in the sample). The decision not to build a daily-dose figure from this is a deliberate scope choice, not an open question.**

---

## Most of the "underdosed" signal isn't creatine underdosing

Of the 268 on-market products under 3g, 224 of them (84%) aren't even named as creatine products. They're mass gainers, whey blends, and similar — creatine's just one ingredient among many, and it was never the point of the product. That's contamination from the ingredient-text match, not evidence that real creatine products are underdosed.

Only 44 products are both named creatine and genuinely under 3g. Of those, 18 look like real, single-serving low-dose products — several cluster right around 2.5g, which matches a pattern already noticed earlier in the project (a handful of brands seem to intentionally dose just under the 3g line). The other 26 are capsule-format products; whether their true daily dose reaches 3g isn't established here, for the same reason described above — this project measures per-serving amount, not daily dose.

**Status: verified on the counts. The 2.5g grouping is a reasonable read of the data, not independently confirmed — call it a pattern, not a fact.**

---

## Why the on-market and mixed-population rates didn't quite match

Earlier, the named-and-under-3g rate looked different on-market (16.4%) versus mixed on/off-market (12.1%), with no explanation. Checked it directly: off-market products are actually *more* dominated by contamination (92.2% not-named-creatine) than on-market ones (83.6%). Discontinued products skew more toward creatine-as-a-minor-ingredient formulas; what's still on shelves skews slightly more toward dedicated creatine products that happen to underdose. Mixing the two populations together diluted the on-market rate.

**Status: verified. Real mechanism, not a coincidence.**

---

## One loose end, left open on purpose

**A magnesium glycinate product (DSLD ID 239649) lists the same ingredient twice**, identical in every column, with no explanation findable in the data. Checked twice, across two different database states, same result both times. This isn't a creatine finding, but it's the clearest example in this dataset of something that just doesn't have an answer, and it's worth keeping visible rather than quietly dropping it.

**Status: open. Not blocking anything, just not pretending to be solved.**

