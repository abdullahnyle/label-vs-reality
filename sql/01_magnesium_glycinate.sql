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