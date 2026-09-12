"""Reproduce the compact amount screens and bounded directions-review totals."""

import argparse
import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

from creatine_directions import REVIEW, candidate_ids, load_review, review_rows, source_record
from creatine_label_checks import check_labels
from creatine_labels import label_amounts
from load_data import sha256


def amount_screen(labels, threshold):
    usable = [row for row in labels if row["min_grams"] is not None]
    return {"labels": len(labels), "usable": len(usable),
            "unresolved": len(labels) - len(usable),
            "partial": sum(row["amount_status"] == "partial" for row in usable),
            "min_at_least": sum(row["min_grams"] >= threshold for row in usable),
            "max_at_least": sum(row["max_grams"] >= threshold for row in usable),
            "crosses": sum(row["min_grams"] < threshold <= row["max_grams"] for row in usable)}


def screens(connection):
    rows = []
    for ignore_case in (False, True):
        labels = list(label_amounts(connection, ignore_case))
        populations = {"all": labels,
                       "on_market": [r for r in labels if r["market_status"] == "On Market"],
                       "off_market": [r for r in labels if r["market_status"] == "Off Market"],
                       "other_status": [r for r in labels if r["market_status"] not in ("On Market", "Off Market")]}
        for population, selected in populations.items():
            for threshold in (3, 2.5):
                rows.append({"matching": "ascii_case_insensitive" if ignore_case else "exact",
                             "population": population, "threshold_g": threshold,
                             **amount_screen(selected, threshold)})
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def reproduce(database, output):
    if output.exists():
        raise ValueError(f"Output already exists: {output}. Choose a new directory.")
    before = sha256(database)
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if integrity != [("ok",)]:
            raise ValueError(f"Database integrity check failed: {integrity[:3]}")
        records, decisions = load_review()
        if candidate_ids(connection) != [r["dsld_id"] for r in records]:
            raise ValueError("Directions candidate set differs from the saved review")
        image_records = [json.loads(line) for line in
                         (REVIEW / "label-checks.jsonl").read_text(encoding="utf-8").splitlines()]
        for record in records + [r["csv"] for r in image_records]:
            if source_record(connection, record["dsld_id"]) != record:
                raise ValueError(f"Review source differs for {record['dsld_id']}")
        reviewed = review_rows(records, decisions)
        label_checks = check_labels()
        amount_rows = screens(connection)
        counts = {"reviewed_labels": len(reviewed),
                  "bands": dict(sorted(Counter(row["band"] for row in reviewed).items())),
                  "scopes": dict(sorted(Counter(row["scope"] for row in reviewed).items())),
                  "image_checked_labels": len(label_checks["checked_ids"]),
                  "csv_api_amount_agreements": label_checks["amount_agreements"]}
        manifest = [dict(zip(("table_name", "file_name", "sha256", "rows", "acquired_on"), row))
                    for row in connection.execute(
                        "SELECT table_name, file_name, sha256, rows, acquired_on "
                        "FROM ImportManifest ORDER BY table_name, file_name")]
        snapshot = {"database_sha256": before, "integrity": "ok",
                    "product_rows": connection.execute("SELECT count(*) FROM ProductOverview").fetchone()[0],
                    "facts_rows": connection.execute("SELECT count(*) FROM DietarySupplementFacts").fetchone()[0],
                    "source_files": len(manifest),
                    "orphaned_facts": connection.execute(
                        "SELECT count(*) FROM DietarySupplementFacts f LEFT JOIN ProductOverview p "
                        "ON f.[DSLD ID]=p.[DSLD ID] WHERE p.[DSLD ID] IS NULL").fetchone()[0]}
    finally:
        connection.close()
    if sha256(database) != before:
        raise ValueError("Database changed during analysis")
    output.mkdir(parents=True)
    write_csv(output / "amount-screens.csv", amount_rows)
    write_csv(output / "source-files.csv", manifest)
    for name, content in (("review-counts.json", counts), ("snapshot.json", snapshot)):
        with (output / name).open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(content, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New directory for result files")
    args = parser.parse_args()
    try:
        reproduce(args.database, args.output)
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(1, f"Reproduction failed: {error}\n")


if __name__ == "__main__":
    main()
