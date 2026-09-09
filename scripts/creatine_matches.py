"""Export creatine ingredient rows without selecting a serving amount."""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

from amounts import parse_amount

HISTORICAL_NAMES = (
    "Creatine Monohydrate",
    "Creapure 100% Ultra Pure Creatine Monohydrate",
    "Creapure 100% pure Creatine Monohydrate",
    "Creapure Creatine Monohydrate",
    "Creapure brand Creatine Monohydrate",
    "Creapure(R) 100% Ultra Pure Concentrated Creatine Monohydrate",
    "L-Creatine Monohydrate",
    "Micro Creatine Monohydrate",
    "Micronized Creatine Monohydrate",
    "Micronized Pure Creatine Monohydrate",
    "micronized Creapure Creatine Monohydrate",
    "HPLC Pure Creatine Monohydrate",
    "PharmaFuse(TM) Creatine Monohydrate",
    "PharmaPure Creatine Monohydrate",
    "OT2 Creatine Monohydrate",
    "Creatine Monohydrate powder",
    "Creatine monohydrate powder",
    "Creatine Monohydrate; Micronized",
    "Creatine Monohydrate; Instantized",
    "Creatine Monohydrate; Powder",
    "Creatine Monohydrate; Pure",
    "Creatine; Micronized",
    "Creatine Mono",
    "instantized & micronized Creatine Monohydrate",
    "ultrapure Creatine Monohydrate",
)
FIELDS = (
    "source_rowid", "dsld_id", "ingredient", "alias_match",
    "explicit_monohydrate", "raw_amount", "raw_unit", "grams", "parse_status",
)


def matched_facts(connection, ignore_case=False):
    # Override the source column's collation so the historical rule stays exact.
    collation = "NOCASE" if ignore_case else "BINARY"
    placeholders = ",".join("?" for _ in HISTORICAL_NAMES)
    query = f"""
        SELECT rowid, [DSLD ID], Ingredient,
               [Amount Per Serving], [Amount Per Serving Unit]
        FROM DietarySupplementFacts
        WHERE Ingredient COLLATE {collation} IN ({placeholders})
        ORDER BY [DSLD ID] COLLATE BINARY, rowid
    """
    for rowid, dsld_id, ingredient, amount, unit in connection.execute(query, HISTORICAL_NAMES):
        grams, status = parse_amount(amount, unit)
        yield dict(zip(FIELDS, (
            rowid, dsld_id, ingredient,
            "exact" if ingredient in HISTORICAL_NAMES else "case_variant",
            int("monohydrate" in ingredient.lower()), amount, unit, grams, status,
        )))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--ignore-case", action="store_true",
                        help="Also include ASCII capitalization variants of the historical names")
    args = parser.parse_args()
    connection = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(matched_facts(connection, args.ignore_case))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
