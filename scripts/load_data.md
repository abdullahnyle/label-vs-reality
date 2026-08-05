# Rebuilding the database

1. Download the full DSLD database as CSV from https://dsld.od.nih.gov 
   (search page → Download → whole database → CSV).
2. Unzip it. You'll get 8 numbered batches per table 
   (ProductOverview_1 through _8, DietarySupplementFacts_1 through _8).
3. Open DB Browser for SQLite, create a new database.
4. Import batch 1 first, for both ProductOverview_1 and 
   DietarySupplementFacts_1: File → Import → Table from CSV file. 
   **Make sure "Column names in first line" is checked** — 
   otherwise columns import as field1, field2... instead of real names.
5. Rename the two imported tables to drop the _1 suffix: 
   ProductOverview_1 → ProductOverview, 
   DietarySupplementFacts_1 → DietarySupplementFacts.
6. Import batches 2 through 8 the same way, but when the import 
   dialog asks for the target table, select the existing 
   ProductOverview or DietarySupplementFacts table instead of 
   creating a new one. This appends each batch's rows into the 
   same table rather than creating separate tables per batch.
7. Verify the full import: SELECT COUNT(*) FROM ProductOverview; 
   should return 214780, matching DSLD's stated total.
8. Products and ingredients join on the shared DSLD ID column.