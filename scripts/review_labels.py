"""Attach recorded review decisions to their source fields and check retrieved API labels."""

import argparse
import csv
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

from load_data import sha256

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def ingredient_rows(items, parents=()):
    for item in items:
        yield item, parents
        yield from ingredient_rows(item.get("nestedRows", []), parents + (item["name"],))


def amount_key(amount, unit):
    if amount is None or str(amount).strip() == "" or unit == "NP":
        return None
    factors = {"g": Decimal(1), "gram(s)": Decimal(1), "mg": Decimal("0.001")}
    return Decimal(str(amount)) * factors[unit.lower()]


def review(run, api_directory, output, reviewed_on):
    if output.exists():
        raise ValueError("Choose a new review directory")
    candidates = {r["dsld_id"]: r for r in read_csv(run / "candidate_review_queue.csv")}
    decisions = read_csv(ROOT / "docs/reviews/candidate-decisions.csv")
    if len(decisions) != len(candidates) or {r["dsld_id"] for r in decisions} != candidates.keys():
        raise ValueError("Candidate decisions do not cover this run exactly")
    labels = {}
    with (run / "source_labels.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            labels[str(record["label"]["DSLD ID"])] = record
    output.mkdir(parents=True)
    reviewed = []
    for decision in decisions:
        label = decision["dsld_id"]
        row = dict(candidates[label], **decision)
        row["review_status"] = "source_text_reviewed"
        row["reviewer"] = "ChatGPT; Abdullah review pending"
        row["reviewed_on"] = reviewed_on
        row["dosage_form"] = labels[label]["label"]["Supplement Form [LanguaL]"]
        row["serving_basis"] = labels[label]["label"]["Serving Size"]
        if decision["units_per_recorded_serving"]:
            grams = Decimal(row["max_grams"])
            units = Decimal(decision["units_per_recorded_serving"])
            row["daily_min_g"] = str(grams * Decimal(decision["daily_units_min"]) / units)
            row["daily_max_g"] = str(grams * Decimal(decision["daily_units_max"]) / units)
        reviewed.append(row)
    write_csv(output / "candidate_review.csv", reviewed)
    with (output / "candidate_context.jsonl").open("w", encoding="utf-8") as stream:
        for label in sorted(candidates):
            stream.write(json.dumps(labels[label], ensure_ascii=False) + "\n")

    sample = {r["dsld_id"]: r for r in read_csv(run / "suggested_use_sample.csv")}
    codes = read_csv(ROOT / "docs/reviews/suggested-use-decisions.csv")
    if len(codes) != len(sample) or {r["dsld_id"] for r in codes} != sample.keys():
        raise ValueError("Suggested Use decisions do not cover this sample exactly")
    write_csv(output / "suggested_use_review.csv", [dict(sample[r["dsld_id"]], **r,
              reviewer="ChatGPT; Abdullah review pending", reviewed_on=reviewed_on,
              review_status="source_text_reviewed") for r in codes])

    aliases = {r["ingredient"] for r in read_csv(ROOT / "config/creatine_aliases.csv")}
    available = {path.stem for path in api_directory.glob("*.json")}
    if candidates.keys() - available:
        raise ValueError("API responses are missing for candidate labels")
    checks, excerpts = [], []
    for path in sorted(api_directory.glob("*.json")):
        api = json.loads(path.read_text())
        label = str(api["id"])
        if label not in labels:
            raise ValueError(f"API label {label} is outside the matched snapshot")
        source = labels[label]["matched_facts"]
        expected = Counter((r["Ingredient"], amount_key(r["Amount Per Serving"], r["Amount Per Serving Unit"]))
                           for r in source)
        actual, context = Counter(), []
        for row, parents in ingredient_rows(api["ingredientRows"]):
            # The DSLD CSV export substitutes semicolons for commas in names.
            name = row["name"].replace(",", ";")
            if name in aliases:
                for quantity in row["quantity"]:
                    actual[(name, amount_key(quantity.get("quantity"), quantity.get("unit")))] += 1
                context.append(dict(name=row["name"], parent_names=parents,
                                    quantities=row["quantity"]))
        checks.append(dict(dsld_id=label, api_url=f"https://api.ods.od.nih.gov/dsld/v9/label/{label}",
                           retrieved_on=reviewed_on, api_sha256=sha256(path),
                           snapshot_rows=sum(expected.values()), api_rows=sum(actual.values()),
                           matched_amounts_agree=actual == expected,
                           interpretation="Amount agreement only; not image or efficacy validation"))
        excerpts.append(dict(dsld_id=label, full_name=api["fullName"],
                             serving_sizes=api["servingSizes"], matched_ingredients=context))
    write_csv(output / "api_checks.csv", checks)
    with (output / "api_context.jsonl").open("w", encoding="utf-8") as stream:
        for row in excerpts:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return dict(candidate_records=len(reviewed), suggested_use_records=len(codes),
                api_records=len(checks), api_disagreements=sum(not r["matched_amounts_agree"] for r in checks))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("api_directory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reviewed-on", required=True)
    args = parser.parse_args()
    print(json.dumps(review(args.run, args.api_directory, args.output, args.reviewed_on), indent=2))
