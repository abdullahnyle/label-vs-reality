import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from amounts import parse_amount
from load_data import load_snapshot

OVERVIEW = ["DSLD ID", "Product Name", "Market Status", "Suggested Use"]
FACTS = ["DSLD ID", "Ingredient", "Amount Per Serving", "Amount Per Serving Unit"]


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


class AmountTests(unittest.TestCase):
    def test_supported_quantities_are_converted_to_grams(self):
        cases = [
            ("3,000", "mg", 3),
            ("4", "g", 4),
            ("2.5", "Gram(s)", 2.5),
            (" .5 ", " G ", 0.5),
        ]
        for amount, unit, expected in cases:
            with self.subTest(amount=amount, unit=unit):
                self.assertEqual(parse_amount(amount, unit), (expected, "usable"))

    def test_ambiguous_and_missing_quantities_are_kept_out(self):
        cases = [
            (None, "g", "missing_amount"),
            ("", "g", "missing_amount"),
            ("5", "", "missing_unit"),
            ("5", "mcg", "unsupported_unit"),
            ("2.5-5", "g", "non_scalar_or_invalid"),
            ("<3", "g", "non_scalar_or_invalid"),
            ("0", "g", "zero_needs_review"),
        ]
        for amount, unit, reason in cases:
            with self.subTest(amount=amount, unit=unit):
                self.assertEqual(parse_amount(amount, unit), (None, reason))


class SnapshotImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.source = self.folder / "source"
        self.source.mkdir()
        write_csv(
            self.source / "ProductOverview_1.csv",
            OVERVIEW,
            [("10", "Plain creatine", "On Market", "Take one scoop daily")],
        )
        write_csv(
            self.source / "DietarySupplementFacts_1.csv",
            FACTS,
            [("10", "Creatine Monohydrate", "3,000", "mg")],
        )

    def test_import_keeps_source_text_and_provenance(self):
        database = self.folder / "snapshot.db"
        result = load_snapshot(self.source, database, "2026-01-10")

        self.assertEqual(len(result["sha256"]), 64)
        with sqlite3.connect(database) as connection:
            product = connection.execute(
                "SELECT [DSLD ID], [Suggested Use] FROM ProductOverview"
            ).fetchone()
            amount = connection.execute(
                "SELECT [Amount Per Serving] FROM DietarySupplementFacts"
            ).fetchone()[0]
            manifest = connection.execute(
                "SELECT file_name, rows, acquired_on FROM ImportManifest ORDER BY file_name"
            ).fetchall()

        self.assertEqual(product, ("10", "Take one scoop daily"))
        self.assertEqual(amount, "3,000")
        self.assertEqual(
            manifest,
            [
                ("DietarySupplementFacts_1.csv", 1, "2026-01-10"),
                ("ProductOverview_1.csv", 1, "2026-01-10"),
            ],
        )

    def test_bad_batch_does_not_leave_a_database(self):
        write_csv(self.source / "ProductOverview_2.csv", OVERVIEW[:-1], [])
        database = self.folder / "bad.db"

        with self.assertRaisesRegex(ValueError, "Header differs"):
            load_snapshot(self.source, database)

        self.assertFalse(database.exists())

    def test_existing_database_is_not_replaced(self):
        database = self.folder / "snapshot.db"
        database.write_bytes(b"existing")

        with self.assertRaisesRegex(ValueError, "already exists"):
            load_snapshot(self.source, database)

        self.assertEqual(database.read_bytes(), b"existing")

    def test_fact_without_a_product_record_is_rejected(self):
        write_csv(
            self.source / "DietarySupplementFacts_1.csv",
            FACTS,
            [("11", "Creatine Monohydrate", "3", "Gram(s)")],
        )
        database = self.folder / "orphaned-fact.db"

        with self.assertRaisesRegex(ValueError, "1 rows without a product record"):
            load_snapshot(self.source, database)

        self.assertFalse(database.exists())

    def test_multiline_directions_are_preserved(self):
        directions = 'Take one scoop daily.\nUse a "level" scoop.'
        write_csv(
            self.source / "ProductOverview_1.csv",
            OVERVIEW,
            [("10", "Plain creatine", "On Market", directions)],
        )
        database = self.folder / "snapshot.db"
        load_snapshot(self.source, database)

        with sqlite3.connect(database) as connection:
            stored = connection.execute(
                "SELECT [Suggested Use] FROM ProductOverview"
            ).fetchone()[0]
        self.assertEqual(stored, directions)


if __name__ == "__main__":
    unittest.main()
