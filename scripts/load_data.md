# Rebuilding the database

1. Download the full DSLD database as CSV from https://dsld.od.nih.gov 
   (search page → Download → whole database → CSV).
2. Unzip it. You'll get numbered batches (ProductOverview_1, 
   DietarySupplementFacts_1, etc. through _8).
3. Open DB Browser for SQLite, create a new database.
4. File → Import → Table from CSV file, for each file you want to load.
   **Make sure "Column names in first line" is checked** — 
   otherwise columns import as field1, field2... instead of real names.
5. Products and ingredients join on the shared `DSLD ID` column.
