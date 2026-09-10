import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_directions import daily_amount, review_rows, source_hash


class DirectionsTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "dsld_id": "7", "name": "Creatine", "suggested_use": "Four capsules daily",
            "creatine_rows": [{"rowid": 10, "ingredient": "Creatine Monohydrate",
                               "amount": "2800", "unit": "mg", "serving": "4 capsules"}],
        }
        self.decision = {
            "dsld_id": "7", "source_sha256": source_hash(self.record), "source_rowid": "10",
            "scope": "daily", "units_per_serving": "4", "daily_units_min": "4",
            "daily_units_max": "4",
        }

    def test_capsule_count_does_not_multiply_the_whole_serving_again(self):
        self.assertEqual(daily_amount(self.record, self.decision), (2.8, 2.8))

    def test_maintenance_range_can_cross_screen(self):
        self.record["creatine_rows"][0].update(amount="2250", serving="3 capsules")
        self.decision.update(source_sha256=source_hash(self.record), scope="maintenance",
                             units_per_serving="3", daily_units_min="3", daily_units_max="5")
        reviewed = review_rows([self.record], [self.decision])[0]
        self.assertEqual((reviewed["daily_min_g"], reviewed["daily_max_g"]), (2.25, 3.75))
        self.assertEqual(reviewed["band"], "crosses_3g")

    def test_changed_directions_invalidate_the_decision(self):
        self.record["suggested_use"] = "Four capsules twice daily"
        with self.assertRaisesRegex(ValueError, "Source changed"):
            daily_amount(self.record, self.decision)

    def test_unresolved_is_not_zero_and_cannot_have_a_calculation(self):
        self.decision["scope"] = "workout_only"
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            daily_amount(self.record, self.decision)
        for field in ("source_rowid", "units_per_serving", "daily_units_min", "daily_units_max"):
            self.decision[field] = ""
        self.assertEqual(daily_amount(self.record, self.decision), (None, None))
        self.assertEqual(review_rows([self.record], [self.decision])[0]["band"], "unresolved")

    def test_missing_and_duplicate_decisions_fail(self):
        for decisions in ([], [self.decision, self.decision]):
            with self.assertRaisesRegex(ValueError, "IDs"):
                review_rows([self.record], decisions)

    def test_bad_units_ranges_and_source_rows_fail(self):
        for field, value in (("units_per_serving", "0"), ("daily_units_min", "nan"),
                             ("daily_units_max", "3"), ("source_rowid", "99"),
                             ("scope", "daIly")):
            decision = copy.copy(self.decision)
            decision[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                daily_amount(self.record, decision)


if __name__ == "__main__":
    unittest.main()
