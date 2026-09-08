-- A daily reference and a per-serving screen answer different questions.
DROP TABLE IF EXISTS temp.CreatineReference;
CREATE TEMP TABLE CreatineReference (
    form TEXT PRIMARY KEY,
    maintenance_low_g_per_day REAL NOT NULL,
    maintenance_high_g_per_day REAL NOT NULL,
    source TEXT NOT NULL,
    context TEXT NOT NULL
);
INSERT INTO CreatineReference VALUES (
    'Creatine Monohydrate', 3.0, 5.0,
    'https://doi.org/10.1186/s12970-017-0173-z',
    'ISSN position stand (2017), Supplementation protocols: typical maintenance '
    || 'after saturation; larger athletes may require 5–10 g/day. '
    || 'This is not a product efficacy or safety classification.'
);
