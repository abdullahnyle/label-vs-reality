import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_positive_value_cannot_underflow_to_usable_zero(self):
        self.assertEqual(parse_amount("0." + "0" * 400 + "1", "g"),
                         (None, "non_scalar_or_invalid"))


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
        for name in ("candidate_review_queue.csv", "suggested_use_sample.csv"):
            with (first / name).open() as stream:
                queue = list(csv.DictReader(stream))
            self.assertTrue(queue)
            self.assertTrue(all(row["review_status"] == "pending" for row in queue))
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

    def test_source_export_keeps_surrounding_facts_and_null_metadata(self):
        con = self.connection()
        con.execute('ALTER TABLE ProductOverview ADD COLUMN analysis_id TEXT')
        con.execute('UPDATE ProductOverview SET analysis_id = \'Original source metadata\'')
        con.execute('UPDATE ProductOverview SET [Product Name] = NULL WHERE [DSLD ID] = \'8\'')
        con.execute('INSERT INTO DietarySupplementFacts VALUES (?,?,?,?,?)',
                    ("8", "Proprietary blend", "10", "g", "parent"))
        con.commit()
        output = self.folder / "context"
        analyze(self.database, output, "Synthetic panel context")
        labels = [json.loads(line) for line in (output / "source_labels.jsonl").read_text().splitlines()]
        label = next(row for row in labels if row["label"]["DSLD ID"] == "8")
        self.assertIsNone(label["label"]["Product Name"])
        self.assertEqual(label["label"]["analysis_id"], "Original source metadata")
        self.assertEqual(len(label["matched_facts"]), 1)
        self.assertEqual({row["Ingredient"] for row in label["other_facts"]},
                         {"Pancreatine Enzyme", "Proprietary blend"})

    def test_alias_matching_ignores_source_nocase_collation(self):
        con = self.connection()
        con.execute('ALTER TABLE DietarySupplementFacts RENAME TO OldFacts')
        con.execute('CREATE TABLE DietarySupplementFacts ([DSLD ID] TEXT, Ingredient TEXT COLLATE NOCASE, [Amount Per Serving] TEXT, [Amount Per Serving Unit] TEXT, Panel TEXT)')
        con.execute('INSERT INTO DietarySupplementFacts SELECT * FROM OldFacts')
        con.execute('DROP TABLE OldFacts')
        con.execute('INSERT INTO DietarySupplementFacts VALUES (?,?,?,?,?)',
                    ("2", "CREATINE MONOHYDRATE", "20", "g", "unmatched spelling"))
        con.commit()
        output = self.folder / "case-sensitive"
        analyze(self.database, output, "Synthetic NOCASE source")
        with (output / "records.csv").open() as stream:
            record = next(row for row in csv.DictReader(stream) if row["dsld_id"] == "2")
        self.assertEqual(float(record["max_grams"]), 2.5)
        self.assertIn("CREATINE MONOHYDRATE", (output / "unmatched_names.csv").read_text())
        with (output / "case_insensitive_records.csv").open() as stream:
            case_record = next(row for row in csv.DictReader(stream) if row["dsld_id"] == "2")
        self.assertEqual(float(case_record["max_grams"]), 20)
        self.assertEqual(int(case_record["matching_rows"]), 3)
        with (output / "case_variants.csv").open() as stream:
            self.assertEqual(list(csv.DictReader(stream)),
                             [{"ingredient": "CREATINE MONOHYDRATE", "source_rows": "1"}])

    def test_sample_order_does_not_depend_on_id_storage_type(self):
        con = self.connection()
        con.execute('INSERT INTO ProductOverview VALUES (?,?,?,?,?)',
                    ("10", "Creatine ten", "On Market", "One serving daily", "1 scoop"))
        con.execute('INSERT INTO DietarySupplementFacts VALUES (?,?,?,?,?)',
                    ("10", "Creatine Monohydrate", "3", "g", "main"))
        con.commit()
        first, second = self.folder / "text-ids", self.folder / "integer-ids"
        analyze(self.database, first, "Synthetic ID storage")
        for table in ("ProductOverview", "DietarySupplementFacts"):
            con.execute(f'ALTER TABLE {table} RENAME TO old_{table}')
            fields = con.execute(f'PRAGMA table_info(old_{table})').fetchall()
            columns = ', '.join('"' + r[1] + '" ' + ('INTEGER' if r[1] == 'DSLD ID' else 'TEXT') for r in fields)
            con.execute(f'CREATE TABLE {table} ({columns})')
            con.execute(f'INSERT INTO {table} SELECT * FROM old_{table}')
            con.execute(f'DROP TABLE old_{table}')
        con.commit()
        analyze(self.database, second, "Synthetic ID storage")
        self.assertEqual((first / "suggested_use_sample.csv").read_bytes(),
                         (second / "suggested_use_sample.csv").read_bytes())

    def test_report_and_sensitivity_expose_partly_unresolved_labels(self):
        output = self.folder / "missingness"
        analyze(self.database, output, "Synthetic partial declarations")
        with (output / "sensitivity.csv").open() as stream:
            summary = list(csv.DictReader(stream))
        row = next(row for row in summary if row["alias_policy"] == "expanded"
                   and row["population"] == "on_market" and row["selection"] == "max")
        self.assertEqual(int(row["partly_unresolved"]), 1)
        self.assertIn("Usable on-market records with additional unresolved declarations: 1.",
                      (output / "report.md").read_text())

    def test_sensitivity_counts_match_fixture_cohorts(self):
        output = self.folder / "sensitivity"
        analyze(self.database, output, "Synthetic sensitivity checks")
        with (output / "sensitivity.csv").open() as stream:
            summary = list(csv.DictReader(stream))
        keyed = {(r["alias_policy"], r["population"], r["selection"],
                  float(r["threshold_g"])): r for r in summary}
        self.assertEqual(len(summary), 72)
        self.assertEqual(len(keyed), 72)
        # Expected counts follow the eight labels in fixture(), not the SQL.
        expected = [
            (("expanded", "all", "max", 3), (8, 6, 4, 2, 2, 1)),
            (("expanded", "all", "min", 3), (8, 6, 3, 3, 2, 1)),
            (("expanded", "on_market", "max", 2.5), (6, 5, 4, 1, 1, 1)),
            (("expanded", "on_market", "max", 5), (6, 5, 1, 4, 1, 1)),
            (("explicit_monohydrate", "on_market", "max", 3), (5, 4, 2, 2, 1, 1)),
            (("expanded", "off_market", "max", 3), (1, 1, 1, 0, 0, 0)),
            (("expanded", "unknown", "max", 3), (1, 0, 0, 0, 1, 0)),
        ]
        fields = ("total", "usable", "at_least_threshold", "below_threshold",
                  "unusable", "partly_unresolved")
        for key, counts in expected:
            with self.subTest(key=key):
                self.assertEqual(tuple(int(keyed[key][f]) for f in fields), counts)
        for row in summary:
            self.assertEqual(int(row["total"]), int(row["usable"]) + int(row["unusable"]))
            self.assertEqual(int(row["usable"]),
                             int(row["at_least_threshold"]) + int(row["below_threshold"]))
            if int(row["usable"]) == 0:
                self.assertEqual(row["percent_of_usable"], "")

    def test_new_wal_activity_discards_outputs(self):
        from analyze import export_evidence
        output = self.folder / "changed"
        wal = Path(str(self.database) + "-wal")

        def export_then_simulate_writer(*args):
            result = export_evidence(*args)
            wal.write_bytes(b"Synthetic concurrent writer marker")
            return result

        with patch("analyze.export_evidence", side_effect=export_then_simulate_writer):
            with self.assertRaisesRegex(ValueError, "writer"):
                analyze(self.database, output, "Synthetic writer activity")
        self.assertFalse(output.exists())
        wal.unlink()

    def test_shadowed_source_rowid_blocks_analysis(self):
        con = self.connection()
        con.execute('ALTER TABLE DietarySupplementFacts ADD COLUMN rowid TEXT')
        with self.assertRaisesRegex(ValueError, "rowid"):
            check_source(con)

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

    def test_import_rejects_malformed_csv_quotes(self):
        for index, row in enumerate(('1,Creatine Monohydrate,3,g,"unfinished',
                                     '1,Creatine Monohydrate,3,g,"main"trailing\n')):
            with self.subTest(row=row):
                path = self.source / "DietarySupplementFacts_1.csv"
                path.write_text(",".join(FACTS) + "\n" + row, encoding="utf-8")
                output = self.folder / f"malformed-{index}.db"
                with self.assertRaises(csv.Error):
                    load_snapshot(self.source, output)
                self.assertFalse(output.exists())

    def test_import_preserves_valid_multiline_quoted_fields(self):
        directions = 'Take one scoop daily.\nUse a "level" scoop.'
        write_csv(self.source / "ProductOverview_2.csv", OVERVIEW,
                  [("9", "Creatine, plain", "On Market", directions, "1 scoop")])
        output = self.folder / "multiline.db"
        load_snapshot(self.source, output)
        with sqlite3.connect(output) as con:
            self.assertEqual(con.execute(
                'SELECT [Suggested Use] FROM ProductOverview WHERE [DSLD ID] = ?',
                ("9",)).fetchone()[0], directions)

    def test_provenance_preserves_raw_market_status_spellings(self):
        con = self.connection()
        con.execute('ALTER TABLE ProductOverview RENAME TO OldOverview')
        con.execute('CREATE TABLE ProductOverview ([DSLD ID] TEXT, [Product Name] TEXT, [Market Status] TEXT COLLATE NOCASE, [Suggested Use] TEXT, [Serving Size] TEXT)')
        con.execute('INSERT INTO ProductOverview SELECT * FROM OldOverview')
        con.execute('DROP TABLE OldOverview')
        con.execute('UPDATE ProductOverview SET [Market Status] = ? WHERE [DSLD ID] = ?',
                    ("ON MARKET", "1"))
        con.commit()
        metadata = analyze(self.database, self.folder / "raw-statuses", "Synthetic status spellings")
        self.assertEqual(metadata["market_statuses"], [
            {"status": "ON MARKET", "records": 1},
            {"status": "Off Market", "records": 1},
            {"status": "On Market", "records": 5},
            {"status": "Unclassified", "records": 1},
        ])

    def test_import_never_overwrites_an_existing_database(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            load_snapshot(self.source, self.database)

    def test_import_does_not_replace_a_destination_created_during_loading(self):
        output = self.folder / "concurrent.db"

        def fingerprint_and_create_destination(path):
            if not output.exists():
                output.write_bytes(b"Another process owns this destination")
            return sha256(path)

        with patch("load_data.sha256", side_effect=fingerprint_and_create_destination):
            with self.assertRaises(FileExistsError):
                load_snapshot(self.source, output)
        self.assertEqual(output.read_bytes(), b"Another process owns this destination")

    def test_import_validates_acquisition_date_before_writing(self):
        output = self.folder / "invalid-date.db"
        with self.assertRaises(ValueError):
            load_snapshot(self.source, output, "2026-02-30")
        self.assertFalse(output.exists())

    def test_invalid_csv_row_discards_import(self):
        write_csv(self.source / "DietarySupplementFacts_1.csv", FACTS,
                  [("1", "Creatine Monohydrate", "3")])
        output = self.folder / "short-row.db"
        with self.assertRaisesRegex(ValueError, "Wrong field count"):
            load_snapshot(self.source, output)
        self.assertFalse(output.exists())

    def test_blank_and_duplicate_source_ids_discard_import(self):
        for product_id, expected_error in [(" ", ValueError), ("1", sqlite3.IntegrityError)]:
            with self.subTest(product_id=product_id):
                write_csv(self.source / "ProductOverview_2.csv", OVERVIEW,
                          [(product_id, "Creatine", "On Market", "Daily", "Scoop")])
                output = self.folder / "bad-ids.db"
                with self.assertRaises(expected_error):
                    load_snapshot(self.source, output)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
