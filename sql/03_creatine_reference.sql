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