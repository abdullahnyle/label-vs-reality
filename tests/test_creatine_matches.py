import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_matches import matched_facts


class CreatineMatchingTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.execute("""
            CREATE TABLE DietarySupplementFacts (
                [DSLD ID] TEXT, Ingredient TEXT COLLATE NOCASE,
                [Amount Per Serving] TEXT, [Amount Per Serving Unit] TEXT
            )
        """)

    def insert_facts(self, facts):
        self.connection.executemany(
            "INSERT INTO DietarySupplementFacts VALUES (?,?,?,?)", facts
        )

    def test_exact_matching_overrides_source_collation(self):
        self.insert_facts([
            ("1", "Creatine Monohydrate", "3", "g"),
            ("2", "creatine monohydrate", "3", "g"),
            ("3", "Creatine HCl", "3", "g"),
            ("4", "Creatine Monohydrate blend", "3", "g"),
        ])
        exact = list(matched_facts(self.connection))
        self.assertEqual([row["dsld_id"] for row in exact], ["1"])
        expanded = list(matched_facts(self.connection, ignore_case=True))
        self.assertEqual([row["dsld_id"] for row in expanded], ["1", "2"])
        self.assertEqual(expanded[1]["alias_match"], "case_variant")

    def test_case_equivalent_aliases_do_not_multiply_source_rows(self):
        self.insert_facts([("5", "Creatine monohydrate powder", "3000", "mg")])
        matched = list(matched_facts(self.connection, ignore_case=True))
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["grams"], 3.0)
        self.assertEqual(matched[0]["raw_amount"], "3000")

    def test_repeated_declarations_and_unresolved_amounts_survive(self):
        self.insert_facts([
            ("6", "Creatine Monohydrate", "2.5", "g"),
            ("6", "Creatine Monohydrate", "5", "g"),
            ("6", "Creatine Monohydrate", "2.5-5", "g"),
            ("7", "Creatine Monohydrate", "", ""),
        ])
        matched = list(matched_facts(self.connection))
        self.assertEqual([row["source_rowid"] for row in matched], [1, 2, 3, 4])
        self.assertEqual([row["grams"] for row in matched], [2.5, 5.0, None, None])
        self.assertEqual(matched[2]["raw_amount"], "2.5-5")
        self.assertEqual(matched[2]["parse_status"], "non_scalar_or_invalid")
        self.assertEqual(matched[3]["parse_status"], "missing_amount")

    def test_historical_shorthand_is_not_explicit_monohydrate(self):
        self.insert_facts([
            ("8", "Creatine Mono", "3", "g"),
            ("9", "Creatine; Micronized", "3", "g"),
            ("10", "Creatine Monohydrate", "3", "g"),
        ])
        flags = {row["ingredient"]: row["explicit_monohydrate"]
                 for row in matched_facts(self.connection)}
        self.assertEqual(flags, {
            "Creatine Mono": 0, "Creatine; Micronized": 0, "Creatine Monohydrate": 1,
        })


if __name__ == "__main__":
    unittest.main()
