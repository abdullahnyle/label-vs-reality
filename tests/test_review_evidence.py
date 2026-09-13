import json
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from creatine_directions import REVIEW, load_review, review_rows
from creatine_label_checks import check_labels


class SavedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.saved = json.loads((REVIEW / "review-counts.json").read_text(encoding="utf-8"))

    def test_saved_directions_totals_match_source_bound_calculations(self):
        rows = review_rows(*load_review())
        self.assertEqual(len(rows), self.saved["reviewed_labels"])
        self.assertEqual(dict(Counter(row["band"] for row in rows)), self.saved["bands"])
        self.assertEqual(dict(Counter(row["scope"] for row in rows)), self.saved["scopes"])

    def test_saved_image_totals_match_checked_excerpts(self):
        checked = check_labels()
        self.assertEqual(len(checked["checked_ids"]), self.saved["image_checked_labels"])
        self.assertEqual(checked["amount_agreements"], self.saved["csv_api_amount_agreements"])


if __name__ == "__main__":
    unittest.main()
