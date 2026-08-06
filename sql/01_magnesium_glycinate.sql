-- Which products contain magnesium glycinate, and how many?
-- Joins ingredient rows (DietarySupplementFacts) to product identity
-- (ProductOverview) on the shared DSLD ID.

SELECT
    f."DSLD ID",
    p."Product Name",
    f."Ingredient",
    f."Amount Per Serving",
    f."Amount Per Serving Unit"
FROM DietarySupplementFacts AS f
JOIN ProductOverview AS p
    ON f."DSLD ID" = p."DSLD ID"
WHERE f."Ingredient" LIKE '%magnesium glycinate%'
ORDER BY f."DSLD ID";
-- Full-dataset re-run (all 8 batches loaded, 214,780 total labels).
-- Batch-1-only result above was 13 rows / 12 products.
-- Full dataset: 136 rows / 125 products.

-- The 11-row gap (136 - 125) was investigated rather than assumed.
-- Classifier: per DSLD ID, compare COUNT(*) to COUNT(DISTINCT [Ingredient]).
-- Equal counts = two different label lines both matched the filter.
-- Distinct count lower than row count = the same ingredient text repeated.
SELECT 
    [DSLD ID], 
    COUNT(*) AS matching_rows,
    COUNT(DISTINCT [Ingredient]) AS distinct_ingredient_text
FROM DietarySupplementFacts
WHERE [Ingredient] LIKE '%magnesium glycinate%'
GROUP BY [DSLD ID]
HAVING COUNT(*) > 1
ORDER BY distinct_ingredient_text, [DSLD ID];

-- Finding: of the 11 duplicate IDs, 10 show a branded blend name
-- (e.g. "Mag Sci Magnesium Glycinate Complex") alongside its own
-- listed sub-ingredient line (e.g. "Magnesium Glycinate"). Both lines
-- contain the matched text, so a single real ingredient gets counted
-- twice by a text filter. One ID (239649) is a genuine exception:
-- the identical ingredient text appears twice on the same label,
-- cause not yet investigated.
--
-- Where a product legitimately contains more than one magnesium form
-- (e.g. ID 81711, glycinate and lysinate together), the forms are
-- clearly and separately named, not a naming collision.
--
-- Net: the 136-row full-dataset count overstates distinct magnesium
-- glycinate products by 11, almost entirely due to blend-naming
-- structure, not real duplication. 125 is the trustworthy product count.

-- Follow-up, Aug 6: closing the open thread on DSLD ID 239649
-- Flagged since Aug 5 as an unexplained duplicate: "Magnesium Glycinate"
-- appears twice on this label, distinct from the 10 blend/complex cases
-- (no "Complex" or blend name present here at all).
--
-- Checked properly this time: pulled every column available for both
-- duplicate rows to see if anything actually distinguished them.
SELECT [Amount Per Serving], [Amount Per Serving Unit],
       [% Daily Value per Serving], [DSLD Ingredient Categories]
FROM DietarySupplementFacts
WHERE [DSLD ID] = 239649
AND [Ingredient] = 'Magnesium Glycinate';

-- Result: both rows are identical in every available column (400 mg,
-- same unit, same category, nothing distinguishes them). No blend
-- structure, no dosage split, nothing in the data explains why this
-- line appears twice.
--
-- Conclusion: this is a genuine, confirmed duplicate with no
-- discoverable cause from the data available. Whether it originates
-- from the manufacturer's label submission or from DSLD's own data
-- entry can't be determined here, and that's the honest answer, not
-- a gap to guess around.
--
-- Note: this was independently reproduced across two different
-- database states, first flagged Aug 5 against the original stacked
-- dataset, then re-confirmed Aug 6 after a full re-import following a
-- data-loss incident that night (batches 2-8 hadn't actually persisted
-- to disk since Aug 5). Same result both times, which rules out
-- tonight's data-loss bug as the cause, though it doesn't rule out
-- something upstream in DSLD's own data.