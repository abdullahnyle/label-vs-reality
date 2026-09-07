-- Run through scripts/analyze.py, which registers strict amount parsing
-- and loads the alias list. Only temporary tables are written.
DROP TABLE IF EXISTS temp.CreatineRecords;
DROP TABLE IF EXISTS temp.CreatineRows;

CREATE TEMP TABLE CreatineRows AS
SELECT
    f.rowid AS source_rowid,
    f.[DSLD ID] AS dsld_id,
    f.Ingredient AS ingredient,
    f.[Amount Per Serving] AS raw_amount,
    f.[Amount Per Serving Unit] AS raw_unit,
    amount_status(f.[Amount Per Serving], f.[Amount Per Serving Unit]) AS parse_status,
    amount_grams(f.[Amount Per Serving], f.[Amount Per Serving Unit]) AS grams
FROM DietarySupplementFacts AS f
JOIN CreatineAliases AS a ON f.Ingredient = a.ingredient
WHERE a.explicit_monohydrate = 1
   OR (SELECT expanded FROM AnalysisOptions) = 1;

CREATE INDEX temp.creatine_rows_id ON CreatineRows(dsld_id);

CREATE TEMP TABLE CreatineRecords AS
WITH quantities AS (
    SELECT dsld_id,
           COUNT(*) AS matching_rows,
           COUNT(grams) AS usable_rows,
           COUNT(*) - COUNT(grams) AS unresolved_rows,
           COUNT(DISTINCT grams) AS distinct_amounts,
           MIN(grams) AS min_grams,
           MAX(grams) AS max_grams
    FROM CreatineRows
    GROUP BY dsld_id
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY dsld_id
        ORDER BY grams IS NULL, grams DESC, source_rowid
    ) AS position
    FROM CreatineRows
)
SELECT q.*, r.source_rowid AS selected_source_rowid,
       p.[Product Name] AS product_name,
       p.[Market Status] AS raw_market_status,
       CASE lower(trim(p.[Market Status]))
           WHEN 'on market' THEN 'on_market'
           WHEN 'off market' THEN 'off_market'
           ELSE 'unknown'
       END AS market_status,
       p.[Suggested Use] AS suggested_use,
       CASE
           WHEN p.[Product Name] IS NULL OR trim(p.[Product Name]) = '' THEN 'missing_name'
           WHEN lower(p.[Product Name]) LIKE '%creatine%' THEN 'name_contains_creatine'
           ELSE 'name_without_creatine'
       END AS name_group,
       CASE
           WHEN q.max_grams IS NULL THEN 'unusable'
           WHEN q.max_grams < 3.0 THEN 'below_3g'
           ELSE 'at_least_3g'
       END AS threshold_category
FROM quantities AS q
JOIN ranked AS r ON q.dsld_id = r.dsld_id AND r.position = 1
JOIN ProductOverview AS p ON q.dsld_id = p.[DSLD ID];
