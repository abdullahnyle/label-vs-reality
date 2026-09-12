-- Historical maintenance reference and ingredient-count query.
-- Use scripts/creatine_results.py for the current amount analysis.
-- The dose reference is daily maintenance after saturation, not a
-- per-serving efficacy cutoff. See docs/creatine-case-study.md.
-- The historical aliases include two names that do not spell out monohydrate.

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
    'General maintenance reference after saturation, not a per-serving efficacy test'
);

UPDATE CreatineFormReference
SET Source = 'Kreider et al. 2017, ISSN position stand, J Int Soc Sports Nutr 14:18, Supplementation protocols. General maintenance after saturation: 3-5 g/day; some larger athletes may need 5-10 g/day. https://doi.org/10.1186/s12970-017-0173-z'
WHERE Form = 'Creatine Monohydrate';

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
