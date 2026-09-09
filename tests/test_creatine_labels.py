import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_labels import label_amounts, on_market_screen


class CreatineLabelTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.executescript("""
            CREATE TABLE ProductOverview (
                [DSLD ID] TEXT, [Product Name] TEXT, [Market Status] TEXT,
                [Suggested Use] TEXT
            );
            CREATE TABLE DietarySupplementFacts (
                [DSLD ID] TEXT, Ingredient TEXT, [Amount Per Serving] TEXT,
                [Amount Per Serving Unit] TEXT
            );
        """)

    def add_label(self, label_id, amounts, market="On Market", use=" ",
                  ingredient="Creatine Monohydrate"):
        self.connection.execute("INSERT INTO ProductOverview VALUES (?,?,?,?)",
                                (label_id, "Test label", market, use))
        self.connection.executemany("INSERT INTO DietarySupplementFacts VALUES (?,?,?,?)",
                                    [(label_id, ingredient, amount, unit)
                                     for amount, unit in amounts])

    def test_converts_before_selecting_and_keeps_tied_source_rows(self):
        self.add_label("1", [("900", "mg"), ("3", "g"), ("3,000", "mg")])
        label = list(label_amounts(self.connection))[0]
        self.assertEqual((label["min_grams"], label["max_grams"]), (0.9, 3.0))
        self.assertEqual(label["min_source_rowids"], "1")
        self.assertEqual(label["max_source_rowids"], "2;3")
        self.assertEqual(label["matched_rows"], 3)

    def test_partial_and_all_unresolved_are_distinct(self):
        self.add_label("1", [("", "g"), ("5", "g")])
        self.add_label("2", [("0", "g"), ("2-5", "g")])
        partial, unresolved = list(label_amounts(self.connection))
        self.assertEqual((partial["amount_status"], partial["unresolved_rows"]), ("partial", 1))
        self.assertEqual((partial["min_grams"], partial["max_grams"]), (5.0, 5.0))
        self.assertEqual((unresolved["amount_status"], unresolved["unresolved_rows"]),
                         ("unresolved", 2))
        self.assertIsNone(unresolved["min_grams"])
        self.assertIsNone(unresolved["max_grams"])
        self.assertEqual(unresolved["max_source_rowids"], "")

    def test_screen_denominators_boundary_missingness_and_market_status(self):
        self.add_label("1", [("2", "g"), ("3", "g")], use="Take as directed")
        self.add_label("2", [("3", "g"), ("", "g")])
        self.add_label("3", [("", "")], use=None)
        self.add_label("4", [("5", "g")], market="Off Market", use="Take daily")
        self.add_label("5", [("5", "g")], market="on market")
        self.assertEqual(on_market_screen(label_amounts(self.connection)), {
            "labels": 3, "usable_labels": 2, "unresolved_labels": 1,
            "partial_labels": 1, "min_at_least_3g": 1, "max_at_least_3g": 2,
            "crosses_3g": 1, "suggested_use_present": 1,
        })

    def test_case_policy_is_shared_with_matching(self):
        self.add_label("1", [("5", "g")], ingredient="micronized Creatine Monohydrate")
        self.assertEqual(list(label_amounts(self.connection)), [])
        self.assertEqual([label["dsld_id"] for label in label_amounts(self.connection, True)], ["1"])

    def test_missing_or_duplicate_overview_fails(self):
        self.add_label("1", [("5", "g")])
        self.connection.execute("DELETE FROM ProductOverview")
        with self.assertRaisesRegex(ValueError, "DSLD ID 1"):
            list(label_amounts(self.connection))
        self.connection.executemany("INSERT INTO ProductOverview VALUES (?,?,?,?)",
                                    [("1", "Test", "On Market", "")] * 2)
        with self.assertRaisesRegex(ValueError, "DSLD ID 1"):
            list(label_amounts(self.connection))


if __name__ == "__main__":
    unittest.main()
