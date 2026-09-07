-- Exploratory chemical reference, not used by the creatine pipeline.
-- Do not multiply a Supplement Facts nutrient amount by these fractions:
-- it may already be elemental magnesium. Verify the source panel and
-- quantity basis before any compound-mass conversion. Chemistry citations
-- and hydration assumptions below still require a separate source review.
-- FDA quantity-basis guidance:
-- https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling

-- MagnesiumFormReference: how much of a labeled compound is actually
-- elemental magnesium, vs. the glycine/oxygen it's bonded to.
-- Standalone lookup table, doesn't pull from ProductOverview or
-- DietarySupplementFacts. Used later to check a product's labeled
-- weight against this to get real elemental mg.
-- Elemental weight only, not absorption/bioavailability, that's a
-- separate and messier question this table isn't trying to answer.

CREATE TABLE MagnesiumFormReference (
    Form TEXT PRIMARY KEY,
    ElementalFraction REAL NOT NULL,
    Source TEXT NOT NULL
);

-- Magnesium Glycinate: Mg (24.31 g/mol) / magnesium glycinate (172.42 g/mol) ~= 14.1%
-- Confirmed via NIST WebBook and PubChem CID 84645.
-- Real range is more like 11-14% depending on hydration state.
-- Some products are also "buffered" with added magnesium oxide to push the
-- on-label number higher, that's not something we can catch from ingredient
-- text alone, so treat this figure as a baseline, not a guarantee.
INSERT INTO MagnesiumFormReference (Form, ElementalFraction, Source)
VALUES (
    'Magnesium Glycinate',
    0.141,
    'NIST WebBook, glycine magnesium salt, MW 172.42 g/mol. Range 11-14% depending on hydration state. Note: some products are "buffered" with added magnesium oxide, which would raise actual elemental content above this figure; not detectable from ingredient text alone.'
);

-- Magnesium Oxide: Mg (24.31 g/mol) / MgO (40.30 g/mol) ~= 60.3%
-- Cross-checked against the Merck Index monograph.
-- "Magnesium Oxide Complex" shows up separately in 2 products (IDs 19713,
-- 31163) and isn't folded in here since we haven't confirmed what it
-- actually is chemically. Open thread.
INSERT INTO MagnesiumFormReference (Form, ElementalFraction, Source)
VALUES (
    'Magnesium Oxide',
    0.603,
    'NIST atomic weights, Mg 24.31 / MgO 40.30 g/mol'
);
