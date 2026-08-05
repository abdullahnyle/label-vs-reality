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
