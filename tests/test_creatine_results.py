import sys
import sqlite3
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_results import amount_screen, reproduce, screens


class AmountScreenTests(unittest.TestCase):
    def test_missing_partial_and_boundary_counts_at_both_thresholds(self):
        labels = [
            {"min_grams": 2.5, "max_grams": 3, "amount_status": "complete"},
            {"min_grams": 2, "max_grams": 2.5, "amount_status": "partial"},
            {"min_grams": None, "max_grams": None, "amount_status": "unresolved"},
        ]
        self.assertEqual(amount_screen(labels, 3), {
            "labels": 3, "usable": 2, "unresolved": 1, "partial": 1,
            "min_at_least": 0, "max_at_least": 1, "crosses": 1})
        self.assertEqual(amount_screen(labels, 2.5), {
            "labels": 3, "usable": 2, "unresolved": 1, "partial": 1,
            "min_at_least": 1, "max_at_least": 2, "crosses": 1})

    def test_empty_market_group_does_not_invent_a_denominator(self):
        self.assertEqual(amount_screen([], 3), {
            "labels": 0, "usable": 0, "unresolved": 0, "partial": 0,
            "min_at_least": 0, "max_at_least": 0, "crosses": 0})

    def test_existing_results_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            saved = output / "amount-screens.csv"
            saved.write_bytes(b"previous results\n")
            with self.assertRaisesRegex(ValueError, "Output already exists"):
                reproduce(output / "unused.db", output)
            self.assertEqual(saved.read_bytes(), b"previous results\n")
            self.assertEqual(list(output.iterdir()), [saved])

    def test_population_and_case_comparisons_use_the_same_converted_rows(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE ProductOverview (
                [DSLD ID] TEXT, [Product Name] TEXT, [Market Status] TEXT,
                [Suggested Use] TEXT);
            CREATE TABLE DietarySupplementFacts (
                [DSLD ID] TEXT, Ingredient TEXT, [Amount Per Serving] TEXT,
                [Amount Per Serving Unit] TEXT);
            INSERT INTO ProductOverview VALUES
                ('1', 'Example', 'On Market', ''),
                ('2', 'Example', 'Off Market', ''),
                ('3', 'Example', NULL, ''),
                ('4', 'Example', 'On Market', '');
            INSERT INTO DietarySupplementFacts VALUES
                ('1', 'Creatine Monohydrate', '900', 'mg'),
                ('1', 'Creatine Monohydrate', '3', 'g'),
                ('2', 'Creatine Monohydrate', '2500', 'mg'),
                ('3', 'Creatine Monohydrate', '', 'g'),
                ('4', 'CREATINE MONOHYDRATE', '3000', 'mg');
        """)
        rows = {(r['matching'], r['population'], r['threshold_g']): r
                for r in screens(connection)}
        exact = rows['exact', 'on_market', 3]
        self.assertEqual((exact['labels'], exact['min_at_least'], exact['max_at_least']),
                         (1, 0, 1))
        variant = rows['ascii_case_insensitive', 'on_market', 3]
        self.assertEqual((variant['labels'], variant['min_at_least'], variant['max_at_least']),
                         (2, 1, 2))
        self.assertEqual(rows['exact', 'off_market', 2.5]['min_at_least'], 1)
        self.assertEqual(rows['exact', 'off_market', 3]['max_at_least'], 0)
        self.assertEqual(rows['exact', 'other_status', 3]['unresolved'], 1)
        self.assertEqual(rows['exact', 'all', 3]['labels'], 3)


if __name__ == "__main__":
    unittest.main()
