"""Summarise recorded creatine amounts by DSLD label ID, not daily intake."""

import argparse
import csv
import json
import sqlite3
import sys
from itertools import groupby
from pathlib import Path

from creatine_matches import matched_facts

LABEL_FIELDS = (
    "dsld_id", "product_name", "market_status", "matched_rows", "unresolved_rows",
    "min_grams", "max_grams", "min_source_rowids", "max_source_rowids",
    "amount_status", "suggested_use_present",
)


def label_amounts(connection, ignore_case=False):
    for dsld_id, declarations in groupby(
            matched_facts(connection, ignore_case), key=lambda row: row["dsld_id"]):
        declarations = list(declarations)
        overview = connection.execute(
            "SELECT [Product Name], [Market Status], [Suggested Use] "
            "FROM ProductOverview WHERE [DSLD ID] COLLATE BINARY = ?", (dsld_id,)
        ).fetchall()
        if len(overview) != 1:
            raise ValueError(f"DSLD ID {dsld_id}: expected one ProductOverview row")
        product_name, market_status, suggested_use = overview[0]
        usable = [row for row in declarations if row["grams"] is not None]
        minimum = min((row["grams"] for row in usable), default=None)
        maximum = max((row["grams"] for row in usable), default=None)
        unresolved = len(declarations) - len(usable)
        status = "unresolved" if not usable else "partial" if unresolved else "complete"
        yield dict(zip(LABEL_FIELDS, (
            dsld_id, product_name, market_status, len(declarations), unresolved,
            minimum, maximum,
            ";".join(str(row["source_rowid"]) for row in usable if row["grams"] == minimum),
            ";".join(str(row["source_rowid"]) for row in usable if row["grams"] == maximum),
            status, int(bool(suggested_use and suggested_use.strip())),
        )))


def on_market_screen(labels):
    counts = dict.fromkeys((
        "labels", "usable_labels", "unresolved_labels", "partial_labels",
        "min_at_least_3g", "max_at_least_3g", "crosses_3g",
        "suggested_use_present",
    ), 0)
    for label in labels:
        if label["market_status"] != "On Market":
            continue
        counts["labels"] += 1
        counts["suggested_use_present"] += label["suggested_use_present"]
        if label["min_grams"] is None:
            counts["unresolved_labels"] += 1
            continue
        counts["usable_labels"] += 1
        counts["partial_labels"] += label["amount_status"] == "partial"
        counts["min_at_least_3g"] += label["min_grams"] >= 3
        counts["max_at_least_3g"] += label["max_grams"] >= 3
        counts["crosses_3g"] += label["min_grams"] < 3 <= label["max_grams"]
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--ignore-case", action="store_true")
    parser.add_argument("--summary", action="store_true",
                        help="Print aggregate on-market 3 g screen counts as JSON")
    args = parser.parse_args()
    connection = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        labels = label_amounts(connection, args.ignore_case)
        if args.summary:
            print(json.dumps(on_market_screen(labels), indent=2))
        else:
            writer = csv.DictWriter(sys.stdout, fieldnames=LABEL_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(labels)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
