import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from amounts import parse_amount
from analyze import analyze, build_analysis, check_source, setup
from load_data import load_snapshot, sha256

OVERVIEW = ["DSLD ID", "Product Name", "Market Status", "Suggested Use", "Serving Size"]
FACTS = ["DSLD ID", "Ingredient", "Amount Per Serving", "Amount Per Serving Unit", "Panel"]


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def fixture(folder):
    labels = [
        ("1", "Creatine mixed units", "On Market", "One serving daily", "See panels"),
        ("2", "Creatine tied quantities", "On Market", "", "1 scoop"),
        ("3", "Blend missing amount", "On Market", " ", "2 scoops"),
        ("4", "Creatine ambiguous form", "On Market", "Take daily", "1 scoop"),
        ("5", "Creatine partial data", "On Market", "Two servings daily", "1 scoop"),
        ("6", "Unresolved zero", "Unclassified", "", "1 capsule"),
        ("7", "Historical creatine", "Off Market", "One serving daily", "1 scoop"),
        ("8", "Creatine boundary", "On Market", "One serving daily", "1 scoop"),
    ]
    quantities = [
        ("1", "Creatine Monohydrate", "500", "mg", "small"),
        ("1", "Creatine Monohydrate", "4", "g", "large"),
        ("2", "Creatine Monohydrate", "2.5", "g", "first"),
        ("2", "Creatine Monohydrate", "2.5", "g", "second"),
        ("3", "Creatine Monohydrate", "", "g", "main"),
        ("3", "Creatine Monohydrate", "100", "mcg", "other"),
        ("4", "Creatine Mono", "5", "g", "main"),
        ("5", "Creatine Monohydrate", "2", "g", "main"),
        ("5", "Creatine Monohydrate", "9-12", "g", "range"),
        ("6", "Creatine Monohydrate", "0", "g", "main"),
        ("7", "Creatine Monohydrate", "6", "g", "main"),
        ("8", "Creatine Monohydrate", "3,000", "mg", "main"),
        ("8", "Pancreatine Enzyme", "9", "g", "main"),
    ]
    write_csv(folder / "ProductOverview_1.csv", OVERVIEW, labels[:4])
    write_csv(folder / "ProductOverview_2.csv", OVERVIEW, labels[4:])
    write_csv(folder / "DietarySupplementFacts_1.csv", FACTS, quantities)


class AmountTests(unittest.TestCase):
    def test_scalar_units(self):
        for raw, unit, expected in [("3,000", "mg", 3), ("4", "g", 4), ("2.5", "Gram(s)", 2.5), (" .5 ", " G ", .5)]:
            with self.subTest(raw=raw, unit=unit):
                self.assertEqual(parse_amount(raw, unit), (expected, "usable"))

    def test_unresolved_values_stay_unresolved(self):
        for raw in (None, "", "not disclosed", "2.5-5", "<3", "3,00", "NaN", "inf", "-2", "0"):
            with self.subTest(raw=raw):
                self.assertIsNone(parse_amount(raw, "g")[0])
        self.assertEqual(parse_amount("5", "mcg")[1], "unsupported_unit")
        self.assertEqual(parse_amount("5", "")[1], "missing_unit")


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.source = self.folder / "source"
        self.source.mkdir()
        fixture(self.source)
        self.database = self.folder / "snapshot.db"
        load_snapshot(self.source, self.database, "2026-09-07")

    def connection(self):
        con = sqlite3.connect(self.database)
        con.row_factory = sqlite3.Row
        self.addCleanup(con.close)
        return con

    def test_ranked_normalized_amounts_and_ties(self):
        con = self.connection()
        check_source(con)
        setup(con)
        data = {r["dsld_id"]: r for r in build_analysis(con)}
        self.assertEqual(len(data), 8)
        self.assertEqual((data["1"]["min_grams"], data["1"]["max_grams"]), (.5, 4))
        self.assertEqual(data["1"]["threshold_category"], "at_least_3g")
        self.assertEqual(data["2"]["matching_rows"], 2)
        self.assertEqual(data["2"]["distinct_amounts"], 1)
        self.assertEqual(data["3"]["threshold_category"], "unusable")
        self.assertEqual(data["5"]["max_grams"], 2)
        self.assertEqual(data["5"]["unresolved_rows"], 1)
        self.assertEqual(data["6"]["market_status"], "unknown")
        self.assertEqual(data["6"]["threshold_category"], "unusable")
        self.assertEqual(data["8"]["threshold_category"], "at_least_3g")
        self.assertEqual(data["8"]["matching_rows"], 1)
        self.assertEqual(data["2"]["selected_source_rowid"], build_analysis(con)[1]["selected_source_rowid"])
        explicit = {r["dsld_id"] for r in build_analysis(con, expanded=False)}
        self.assertEqual(explicit, set(data) - {"4"})

    def test_complete_runs_are_repeatable_and_preserve_source(self):
        before = sha256(self.database)
        first, second = self.folder / "first", self.folder / "second"
        metadata = analyze(self.database, first, "Synthetic test fixture")
        analyze(self.database, second, "Synthetic test fixture")
        self.assertEqual(sha256(self.database), before)
        self.assertEqual(metadata["candidate_reviews_pending"], 2)
        self.assertEqual(metadata["source_counts"]["ProductOverview"], 8)
        for path in first.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes(), path.name)
        with (first / "sensitivity.csv").open() as stream:
            summary = list(csv.DictReader(stream))
        result = next(r for r in summary if r["alias_policy"] == "expanded" and r["population"] == "on_market" and r["selection"] == "max" and r["threshold_g"] == "3.0")
        self.assertEqual([result[k] for k in ("total", "usable", "at_least_threshold", "below_threshold", "unusable")], ["6", "5", "3", "2", "1"])
        for row in summary:
            self.assertEqual(int(row["total"]), sum(int(row[k]) for k in ("at_least_threshold", "below_threshold", "unusable")))
        label = json.loads((first / "source_labels.jsonl").read_text().splitlines()[0])
        self.assertEqual(label["label"]["Serving Size"], "See panels")
        self.assertEqual({r["Panel"] for r in label["matched_facts"]}, {"small", "large"})
        with self.assertRaisesRegex(ValueError, "already exists"):
            analyze(self.database, first, "Synthetic test fixture")

    def test_orphan_rows_block_analysis(self):
        con = self.connection()
        con.execute('INSERT INTO DietarySupplementFacts VALUES (?,?,?,?,?)', ("999", "Creatine Monohydrate", "3", "g", "main"))
        con.commit()
        with self.assertRaisesRegex(ValueError, "no ProductOverview"):
            check_source(con)

    def test_duplicate_ids_block_analysis(self):
        con = self.connection()
        con.execute('DROP INDEX product_id')
        con.execute('INSERT INTO ProductOverview SELECT * FROM ProductOverview WHERE [DSLD ID] = \'1\'')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            check_source(con)

    def test_empty_match_still_exports_headers(self):
        con = self.connection()
        con.execute('DELETE FROM DietarySupplementFacts')
        con.commit()
        output = self.folder / "empty"
        metadata = analyze(self.database, output, "Empty synthetic test fixture")
        self.assertEqual(metadata["matched_ids"], 0)
        self.assertIn("dsld_id", (output / "records.csv").read_text())
        self.assertIn("undefined", (output / "report.md").read_text())

    def test_import_rejects_changed_batch_headers(self):
        write_csv(self.source / "ProductOverview_2.csv", OVERVIEW[:-1], [])
        output = self.folder / "bad.db"
        with self.assertRaisesRegex(ValueError, "Header differs"):
            load_snapshot(self.source, output)
        self.assertFalse(output.exists())

    def test_import_never_overwrites_an_existing_database(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            load_snapshot(self.source, self.database)


if __name__ == "__main__":
    unittest.main()
