-- supplements.db, all 8 DSLD batches loaded (214,780 rows, checked against the
-- usual benchmarks at the start of this session). MagnesiumFormReference already
-- shipped in beef942. This adds CreatineFormReference as its own table, separate
-- from magnesium's, since creatine and Turkesterone (coming later) need different
-- columns than magnesium does.

CREATE TABLE CreatineFormReference (
    Form TEXT PRIMARY KEY,
    EffectiveDose TEXT,
    Source TEXT,
    EvidenceStrength TEXT
);

INSERT INTO CreatineFormReference (Form, EffectiveDose, Source, EvidenceStrength)
VALUES (
    'Creatine Monohydrate',
    '3-5 grams per day',
    'Kreider et al. 2017, ISSN position stand, J Int Soc Sports Nutr 14:18',
    'Strong (decades of RCTs, safety established up to 30g/day)'
);

-- Checked the 3-5g/day figure against the actual ISSN source rather than trusting
-- memory. That's the maintenance dose specifically, not the same thing as the
-- optional loading phase (20-25g/day for about a week). Maintenance is the number
-- that's actually comparable to what a product label states, since labels give a
-- daily dose, not a loading protocol.

UPDATE CreatineFormReference
SET Source = 'Kreider et al. 2017, ISSN position stand, J Int Soc Sports Nutr 14:18. 3-5g/day dose does not scale meaningfully with body size for most adults. Individuals with exceptionally high lean mass (100kg+) may theoretically benefit from up to 5-10g/day, though ISSN does not recommend exceeding 5g/day for the general population and most high-mass individuals still use 5g.'
WHERE Form = 'Creatine Monohydrate';

-- Pulled every product in DSLD whose ingredient text is genuinely "creatine
-- monohydrate," using an exact list rather than a loose LIKE match. Left out
-- Kre-Alkalyn and other buffered forms on purpose, they carry a different labeled
-- dose (1.5-3g/day) and that's a separate question for later. Also left out
-- "Creatine Monohydrate HCL," the name is ambiguous and it's not clear if that's a
-- real hybrid or a data entry quirk. Every other named form (HCl, Ethyl Ester, AKG,
-- Malate, Citrate, Nitrate, Magnesium Chelate, and all the proprietary blends) is
-- excluded too, along with "Pancreatine Enzyme," which only matched because of the
-- wildcard search and isn't creatine at all.
--
-- Result: 2,529 rows, 2,163 distinct products.
--
-- Still open: about 366 products show up more than once (some DSLD IDs appear
-- exactly 3 times). Haven't looked into why yet, could be a real duplicate or
-- something structural. Next session.
--
-- Also still open: this only confirms the ingredient name matched. It doesn't yet
-- check whether these products actually label 3-5g/day like they should. That
-- comparison is the real finding and hasn't happened yet.

SELECT COUNT(*) AS total_rows, COUNT(DISTINCT [DSLD ID]) AS distinct_products
FROM DietarySupplementFacts
WHERE [Ingredient] IN (
    'Creatine Monohydrate',
    'Creapure 100% Ultra Pure Creatine Monohydrate',
    'Creapure 100% pure Creatine Monohydrate',
    'Creapure Creatine Monohydrate',
    'Creapure brand Creatine Monohydrate',
    'Creapure(R) 100% Ultra Pure Concentrated Creatine Monohydrate',
    'L-Creatine Monohydrate',
    'Micro Creatine Monohydrate',
    'Micronized Creatine Monohydrate',
    'Micronized Pure Creatine Monohydrate',
    'micronized Creapure Creatine Monohydrate',
    'HPLC Pure Creatine Monohydrate',
    'PharmaFuse(TM) Creatine Monohydrate',
    'PharmaPure Creatine Monohydrate',
    'OT2 Creatine Monohydrate',
    'Creatine Monohydrate powder',
    'Creatine monohydrate powder',
    'Creatine Monohydrate; Micronized',
    'Creatine Monohydrate; Instantized',
    'Creatine Monohydrate; Powder',
    'Creatine Monohydrate; Pure',
    'Creatine; Micronized',
    'Creatine Mono',
    'instantized & micronized Creatine Monohydrate',
    'ultrapure Creatine Monohydrate'
);

-- Dose distribution, run against the 1,511 products with usable dose data
-- (2,163 minus the 652 with a null Amount Per Serving or unit). Converted
-- everything to grams first (mg / 1000, Gram(s) and g treated the same).
--
-- Roughly 999 distinct products land in the 3-5g reference range, 651 land
-- under 3g, 89 land over 5g. The under-3g number looked bad at first read,
-- but it turned out to be misleading.
--
-- Pulled a sample of the under-3g rows and found a real problem: a lot of
-- them aren't creatine products at all. Serious Mass (a mass gainer) lists
-- 1g of creatine inside a 334g serving. Same pattern in several whey and
-- post-workout blends, and one cleanse product (Mega Clean Herbal Cleanse)
-- that has nothing to do with creatine and only matched because of the
-- ingredient text. These products were never trying to deliver an effective
-- creatine dose, creatine is just one ingredient among many, so measuring
-- them against the 3-5g reference isn't a fair comparison.
--
-- Still open: how to separate genuine creatine products from products that
-- only include creatine as a minor ingredient. A name-based filter
-- (Product Name mentions "creatine") isn't reliable on its own, since some
-- pre-workout blends without "creatine" in the name still dose it properly
-- (AC8 Pre Workout, 3g in a 16g serving; A Bomb, 5g in a 21.4g serving).
-- A ratio-based cutoff was considered but not locked, since picking a
-- specific threshold (0.7? 0.75?) without a real basis would just be a
-- guess dressed up as a rule. Next step instead: look at raw dose amount
-- directly (effective vs not, regardless of what else is in the product),
-- which doesn't require inventing a threshold.

-- Sharpened the dose-status split using a raw dose cutoff instead of a ratio
-- (avoids picking an arbitrary threshold). A product counts as delivering an
-- effective dose if it has >=3g of creatine, regardless of serving size or
-- what else is in the product.
--
-- Result: 1,038 distinct products hit >=3g (effective), 651 fall under it.
--
-- Split the 651 by whether the product name mentions creatine. 581 (about
-- 89%) don't, confirming most of the "underdosed" signal is really the
-- blend/gainer contamination flagged earlier, not real underdosing. Only 70
-- products are actually named as creatine and still come in under 3g.
--
-- Checked those 70 directly. About half (33) are capsule products, where a
-- single serving being under 3g is likely by design, most capsule creatine
-- is meant to be taken as several capsules across a day, not one serving as
-- the full dose. Not confirmed yet, since we haven't checked whether the
-- labeled daily total reaches 3g, just flagging the likely explanation.
--
-- The other 37 are powder or other formats. A few are near-misses close to
-- 3g (Creatine-X at 2.5g), a few still look blend-like despite having
-- "creatine" in the name (Amplified Creatine XXX Power, 1.51g in an 8.39g
-- serving) and slipped past the name filter, and some appear to be genuinely
-- low-dosed dedicated creatine products. Not yet split apart individually.
--
-- Current honest picture: roughly 69% of matched products with usable dose
-- data deliver an effective creatine dose. Of the remainder, most are
-- contamination (wrong product category), a chunk are capsule products
-- where the serving math likely explains the low number, and a small,
-- unresolved group appears to be real underdosing or near-misses. That
-- small group hasn't been individually verified yet.

-- Checked whether 2.5g should replace 3g as the effective-dose cutoff, since a
-- cluster of real products landed right at 2.5g in the previous check. Result:
-- 1,115 distinct products hit >=2.5g versus 1,038 at >=3g, a real jump of
-- about 77 products, roughly 69% effective moving to roughly 74%.
--
-- This does NOT mean 2.5g should replace 3g as the reference dose. The
-- CreatineFormReference table stays at 3-5g/day, that's what the ISSN source
-- actually states, and the reference shouldn't be adjusted to match what
-- products happen to do. What the 2.5g check actually shows is narrower: a
-- real cluster of products cluster right at 2.5g (Creatine SAP, Creatine XS,
-- Creatine-X, Creatine Freak, Six Point Creatine, several others), which
-- looks like a common, intentional industry dose choice sitting just under
-- the 3g line, not a failure to hit the target. Worth noting as a pattern in
-- the eventual write-up, not as grounds to move the reference number.
--
-- Also worth noting: lowering the cutoff doesn't touch the contamination
-- problem. The 503 products still under 2.5g are largely the same
-- mass-gainer/whey/blend contamination already documented, moving the line
-- rescues the near-miss cluster, it doesn't clean up the wrong-category
-- products sitting underneath it.
-- Investigated the 366 products that showed up more than once in the original
-- match (some DSLD IDs appeared exactly 3 times). Pulled full rows for a few
-- of them (182876, 209975, 268422) to see what was actually going on.
--
-- These aren't duplicates in the 239649 sense at all. Each one is a single
-- product that lists its full nutrition panel more than once because the
-- label offers more than one serving size. 182876 and 268422 are mass gainers
-- with a 285g and a 570g serving option, and every nutrient on the label,
-- creatine included, scales in exact proportion between the two (5g creatine
-- at 285g, 10g at 570g, same ratio holding across calories, protein,
-- vitamins, everything). 209975 is a pre-workout with three scoop sizes
-- (5.1g, 7.65g, 15.3g), same pattern, creatine and every other ingredient
-- scaling proportionally across all three.
--
-- This is a real structural feature of the data, not an error, and it's good
-- news for trusting the underlying numbers. But it does mean something for
-- the dose analysis specifically: a single product can show up in both the
-- "effective dose" and "under 3g" buckets at the same time, depending on
-- which serving-size row got counted (182876 has a 5g row and a 10g row for
-- the same underlying product). All the distinct-product counts run tonight
-- may include some of this cross-bucket overlap. Worth resolving before the
-- final write-up, likely by picking one serving size per product (probably
-- the smallest, single-serving option) rather than counting every size
-- option as if it were a separate data point.
--
-- One smaller thread inside this: 182876 shows two 570g rows both listing
-- exactly 10g creatine, identical to each other. Not investigated further,
-- could be a genuine repeat entry or something about how DSLD records
-- product variants. Low priority given the larger finding above.