"""Compare the saved database with a CSV rebuild and independently check its results."""

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from itertools import zip_longest
from pathlib import Path

from load_data import quote, sha256


def canonical(value, numeric=False):
    if value is None or str(value).strip() == "":
        return None
    value = str(value).strip()
    if numeric:
        try:
            return Decimal(value)
        except InvalidOperation:
            pass
    return value


def compare_sources(saved, rebuilt):
    result = {}
    for table in ("ProductOverview", "DietarySupplementFacts"):
        columns = [r[1] for r in saved.execute(f"PRAGMA table_info({quote(table)})")]
        other = [r[1] for r in rebuilt.execute(f"PRAGMA table_info({quote(table)})")]
        if columns != other:
            raise ValueError(f"Different columns in {table}")
        raw_differences, substantive = Counter(), Counter()
        count = 0
        for left, right in zip_longest(saved.execute(f"SELECT * FROM {quote(table)} ORDER BY rowid"),
                                      rebuilt.execute(f"SELECT * FROM {quote(table)} ORDER BY rowid")):
            if left is None or right is None:
                raise ValueError(f"Different row counts in {table}")
            count += 1
            for column, a, b in zip(columns, left, right):
                if a != b:
                    raw_differences[column] += 1
                numeric = column in ("DSLD ID", "Amount Per Serving")
                if canonical(a, numeric) != canonical(b, numeric):
                    substantive[column] += 1
        result[table] = dict(rows=count, raw_differences=dict(raw_differences),
                             differences_after_normalization=dict(substantive))
    return result


def check_amounts(con, run):
    aliases = {r["ingredient"] for r in csv.DictReader(
        (Path(__file__).resolve().parents[1] / "config/creatine_aliases.csv").open())}
    quantities, matched = defaultdict(list), Counter()
    # This cross-check covers the numeric scalars actually observed in this
    # snapshot. It is not a replacement for the production text parser.
    factors = {"g": Decimal(1), "gram(s)": Decimal(1), "mg": Decimal("0.001")}
    for label, name, amount, unit in con.execute(
            'SELECT [DSLD ID], Ingredient, [Amount Per Serving], [Amount Per Serving Unit] FROM DietarySupplementFacts'):
        if name not in aliases:
            continue
        label = str(label)
        matched[label] += 1
        if amount is None or str(amount).strip() == "":
            continue
        if str(unit).strip().lower() not in factors:
            raise ValueError(f"Reference check needs an explicit rule for unit {unit!r}")
        value = Decimal(str(amount).strip()) * factors[str(unit).strip().lower()]
        if not value.is_finite() or value <= 0:
            raise ValueError(f"Reference check needs review of label {label}")
        quantities[label].append(value)
    records = {r["dsld_id"]: r for r in csv.DictReader((run / "records.csv").open())}
    if records.keys() != matched.keys():
        raise ValueError("Reference and pipeline matched different IDs")
    for label, row in records.items():
        values = quantities[label]
        expected = (len(values), min(values) if values else None,
                    max(values) if values else None)
        actual = (int(row["usable_rows"]), canonical(row["min_grams"], True),
                  canonical(row["max_grams"], True))
        if expected != actual or int(row["matching_rows"]) != matched[label]:
            raise ValueError(f"Reference and pipeline disagree on label {label}")
    return dict(matched_rows=sum(matched.values()), matched_ids=len(matched),
                records_checked=len(records), discrepancies=0)


def verify(saved, rebuilt, run):
    before = [sha256(saved), sha256(rebuilt)]
    a = sqlite3.connect(saved.resolve().as_uri() + "?mode=ro", uri=True)
    b = sqlite3.connect(rebuilt.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        checks = {"saved_integrity": a.execute("PRAGMA integrity_check").fetchone()[0],
                  "rebuilt_integrity": b.execute("PRAGMA integrity_check").fetchone()[0],
                  "tables": compare_sources(a, b), "independent_amount_check": check_amounts(b, run)}
    finally:
        a.close()
        b.close()
    if before != [sha256(saved), sha256(rebuilt)]:
        raise ValueError("A source database changed during verification")
    checks.update(saved_sha256=before[0], rebuilt_sha256=before[1], sources_unchanged=True)
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("saved", type=Path)
    parser.add_argument("rebuilt", type=Path)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.saved, args.rebuilt, args.run), indent=2))
