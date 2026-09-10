"""Compare the seven saved API excerpts with CSV declarations and verify source files."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from amounts import parse_amount
from creatine_directions import REVIEW, source_hash
from creatine_matches import HISTORICAL_NAMES


def api_declarations(rows):
    declarations = []
    for row in rows:
        if row["name"] in HISTORICAL_NAMES:
            declarations.append({"ingredient": row["name"], "quantity": row.get("quantity", [])})
        declarations.extend(api_declarations(row.get("nestedRows", [])))
    return declarations


def api_excerpt(response):
    return {"dsld_id": str(response["id"]), "serving_sizes": response["servingSizes"],
            "directions": [row for row in response["statements"]
                           if row["type"] == "Suggested/Recommended/Usage/Directions"],
            "declarations": api_declarations(response["ingredientRows"])}


def amount_pairs(record, api):
    csv_amounts = Counter()
    for row in record["creatine_rows"]:
        if row["ingredient"] in HISTORICAL_NAMES:
            grams, _ = parse_amount(row["amount"], row["unit"])
            if grams is None:
                raise ValueError("This bounded comparison requires usable CSV quantities")
            csv_amounts[row["ingredient"], grams] += 1
    api_amounts = Counter()
    for row in api["declarations"]:
        for quantity in row["quantity"]:
            grams, _ = parse_amount(quantity["quantity"], quantity["unit"])
            if grams is None or quantity["operator"] != "=":
                raise ValueError("This bounded comparison requires scalar API quantities")
            api_amounts[row["ingredient"], grams] += 1
    return csv_amounts, api_amounts


def check_labels(folder=REVIEW, source_dir=None):
    records = [json.loads(line) for line in (folder / "label-checks.jsonl").read_text().splitlines()]
    ids = [record["csv"]["dsld_id"] for record in records]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate label checks")
    for record in records:
        label_id = record["csv"]["dsld_id"]
        if record["api"]["dsld_id"] != label_id:
            raise ValueError("CSV and API label IDs differ")
        if source_hash(record["csv"]) != record["csv_sha256"]:
            raise ValueError(f"CSV excerpt changed for {label_id}")
        csv_amounts, api_amounts = amount_pairs(record["csv"], record["api"])
        if not csv_amounts or csv_amounts != api_amounts:
            raise ValueError(f"CSV/API amounts differ for {label_id}")
        if source_dir:
            api_path = source_dir / "live-labels" / f"{label_id}.json"
            pdf_path = source_dir / "label-pdfs" / f"{label_id}.pdf"
            for path, expected in ((api_path, record["api_sha256"]), (pdf_path, record["pdf_sha256"])):
                if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                    raise ValueError(f"Saved source fingerprint differs: {path.name}")
            if api_excerpt(json.loads(api_path.read_text())) != record["api"]:
                raise ValueError(f"API excerpt differs for {label_id}")
    return {"checked_ids": ids, "amount_agreements": len(ids),
            "source_files_verified": source_dir is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Folder containing live-labels/ and label-pdfs/")
    args = parser.parse_args()
    print(json.dumps(check_labels(source_dir=args.source_dir), indent=2))


if __name__ == "__main__":
    main()
