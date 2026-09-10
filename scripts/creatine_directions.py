"""Check the bounded directions review against saved excerpts or the CSV import."""

import argparse
import csv
import hashlib
import json
import math
import sqlite3
from pathlib import Path

from amounts import parse_amount
from creatine_labels import label_amounts
from creatine_matches import HISTORICAL_NAMES

REVIEW = Path(__file__).resolve().parents[1] / "data" / "creatine-review"
DAILY_SCOPES = {"daily", "maintenance", "normal_training"}
UNRESOLVED_SCOPES = {"missing_directions", "frequency_unspecified", "self_selected",
                     "workout_only", "serving_uncertain", "source_conflict"}


def source_record(connection, dsld_id):
    overview = connection.execute(
        'SELECT [Product Name], [Market Status], "Supplement Form [LanguaL]", '
        "[Serving Size], [Suggested Use], URL FROM ProductOverview WHERE [DSLD ID]=?",
        (dsld_id,),
    ).fetchone()
    if overview is None:
        raise ValueError(f"Missing overview for {dsld_id}")
    facts = connection.execute(
        "SELECT rowid, Ingredient, [Amount Per Serving], [Amount Per Serving Unit], "
        "[Serving Size] FROM DietarySupplementFacts WHERE [DSLD ID]=? ORDER BY rowid",
        (dsld_id,),
    )
    return {
        "dsld_id": dsld_id,
        **dict(zip(("name", "market_status", "form", "overview_serving", "suggested_use", "url"), overview)),
        "creatine_rows": [dict(zip(("rowid", "ingredient", "amount", "unit", "serving"), row))
                          for row in facts if "creatin" in row[1].lower()],
    }


def source_hash(record):
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def candidate_ids(connection):
    return [row["dsld_id"] for row in label_amounts(connection)
            if row["market_status"] == "On Market" and "creatine" in row["product_name"].lower()
            and row["max_grams"] is not None and row["max_grams"] < 3]


def daily_amount(record, decision):
    if decision["scope"] not in DAILY_SCOPES | UNRESOLVED_SCOPES:
        raise ValueError("Unknown directions scope")
    if source_hash(record) != decision["source_sha256"]:
        raise ValueError(f"Source changed for {record['dsld_id']}")
    fields = ("source_rowid", "units_per_serving", "daily_units_min", "daily_units_max")
    if decision["scope"] not in DAILY_SCOPES:
        if any(decision[field] for field in fields):
            raise ValueError("Unresolved directions must not carry a daily calculation")
        return None, None
    selected = [row for row in record["creatine_rows"]
                if str(row["rowid"]) == decision["source_rowid"]]
    if len(selected) != 1 or selected[0]["ingredient"] not in HISTORICAL_NAMES:
        raise ValueError("Daily calculation must use one matched ingredient declaration")
    grams, _ = parse_amount(selected[0]["amount"], selected[0]["unit"])
    if grams is None:
        raise ValueError("Selected declaration has no usable amount")
    serving, low, high = (float(decision[field]) for field in fields[1:])
    if not all(math.isfinite(x) and x > 0 for x in (serving, low, high)) or low > high:
        raise ValueError("Invalid serving or daily units")
    return grams * low / serving, grams * high / serving


def review_rows(records, decisions):
    by_id = {row["dsld_id"]: row for row in records}
    ids = [row["dsld_id"] for row in decisions]
    if len(by_id) != len(records) or len(set(ids)) != len(ids) or set(ids) != set(by_id):
        raise ValueError("Review IDs must match the excerpts exactly, without duplicates")
    reviewed = []
    for decision in decisions:
        record = by_id[decision["dsld_id"]]
        low, high = daily_amount(record, decision)
        band = ("unresolved" if low is None else "below_3g" if high < 3
                else "at_least_3g" if low >= 3 else "crosses_3g")
        reviewed.append({"dsld_id": record["dsld_id"], "name": record["name"],
                         "scope": decision["scope"], "daily_min_g": low,
                         "daily_max_g": high, "band": band})
    return reviewed


def load_review(folder=REVIEW):
    records = [json.loads(line) for line in (folder / "directions-source.jsonl").read_text().splitlines()]
    with (folder / "directions.csv").open(newline="") as stream:
        decisions = list(csv.DictReader(stream))
    return records, decisions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, help="Also check selection and excerpts against the original import")
    args = parser.parse_args()
    records, decisions = load_review()
    if args.database:
        connection = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            if candidate_ids(connection) != [row["dsld_id"] for row in records]:
                raise ValueError("Candidate selection differs from the saved review")
            for record in records:
                if source_record(connection, record["dsld_id"]) != record:
                    raise ValueError(f"Excerpt differs from database for {record['dsld_id']}")
        finally:
            connection.close()
    print(json.dumps(review_rows(records, decisions), indent=2))


if __name__ == "__main__":
    main()
