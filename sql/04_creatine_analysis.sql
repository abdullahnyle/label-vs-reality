-- Exploratory market-status and raw-unit counts for the historical aliases.
-- These queries do not select serving amounts or calculate daily intake.
-- The old raw-amount ranking and out-of-scope CTE queries were removed.
-- Use scripts/creatine_results.py for converted minimum/maximum comparisons.

SELECT p.[Market Status], COUNT(*) AS row_count, COUNT(DISTINCT p.[DSLD ID]) AS distinct_products
FROM DietarySupplementFacts AS f
JOIN ProductOverview AS p ON f.[DSLD ID] = p.[DSLD ID]
WHERE f.[Ingredient] IN (
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
)
GROUP BY p.[Market Status]
ORDER BY row_count DESC;

SELECT DISTINCT [Amount Per Serving Unit], COUNT(*) AS row_count
FROM DietarySupplementFacts
WHERE [Ingredient] IN (
    'Creatine Monohydrate', 'Creapure 100% Ultra Pure Creatine Monohydrate',
    'Creapure 100% pure Creatine Monohydrate', 'Creapure Creatine Monohydrate',
    'Creapure brand Creatine Monohydrate',
    'Creapure(R) 100% Ultra Pure Concentrated Creatine Monohydrate',
    'L-Creatine Monohydrate', 'Micro Creatine Monohydrate',
    'Micronized Creatine Monohydrate', 'Micronized Pure Creatine Monohydrate',
    'micronized Creapure Creatine Monohydrate', 'HPLC Pure Creatine Monohydrate',
    'PharmaFuse(TM) Creatine Monohydrate', 'PharmaPure Creatine Monohydrate',
    'OT2 Creatine Monohydrate', 'Creatine Monohydrate powder',
    'Creatine monohydrate powder', 'Creatine Monohydrate; Micronized',
    'Creatine Monohydrate; Instantized', 'Creatine Monohydrate; Powder',
    'Creatine Monohydrate; Pure', 'Creatine; Micronized', 'Creatine Mono',
    'instantized & micronized Creatine Monohydrate', 'ultrapure Creatine Monohydrate'
)
GROUP BY [Amount Per Serving Unit]
ORDER BY row_count DESC;
