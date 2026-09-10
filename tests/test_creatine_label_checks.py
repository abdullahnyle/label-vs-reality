import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_label_checks import amount_pairs, api_declarations


class LabelSourceTests(unittest.TestCase):
    def setUp(self):
        self.csv = {"creatine_rows": [{"ingredient": "Creatine Monohydrate",
                                     "amount": "3000", "unit": "mg", "serving": "2 capsules"}]}
        self.api = {"declarations": [{"ingredient": "Creatine Monohydrate", "quantity": [
            {"quantity": 3, "unit": "Gram(s)", "operator": "=", "servingSizeQuantity": 1}]}]}

    def test_unit_conversion_agrees_without_validating_serving_metadata(self):
        csv_amounts, api_amounts = amount_pairs(self.csv, self.api)
        self.assertEqual(csv_amounts, api_amounts)
        self.assertEqual(csv_amounts["Creatine Monohydrate", 3.0], 1)

    def test_repeated_quantities_are_not_lost_in_a_set(self):
        self.csv["creatine_rows"].append(self.csv["creatine_rows"][0].copy())
        csv_amounts, api_amounts = amount_pairs(self.csv, self.api)
        self.assertNotEqual(csv_amounts, api_amounts)

    def test_parent_blend_is_not_substituted_for_nested_ingredient(self):
        rows = [{"name": "Creatine blend", "quantity": [{"quantity": 5}], "nestedRows": [
            {"name": "Creatine Monohydrate", "quantity": [{"quantity": 2}]}]}]
        self.assertEqual(api_declarations(rows), [
            {"ingredient": "Creatine Monohydrate", "quantity": [{"quantity": 2}]}])

    def test_inequalities_are_not_equalities(self):
        self.api["declarations"][0]["quantity"][0]["operator"] = "<"
        with self.assertRaisesRegex(ValueError, "scalar"):
            amount_pairs(self.csv, self.api)


if __name__ == "__main__":
    unittest.main()
