"""Exercise the pipeline at synthetic snapshot scale; this is not DSLD data."""

import argparse
import csv
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analyze import analyze
from load_data import load_snapshot, sha256


def benchmark(labels, facts_per_label, match_every, unindexed):
    with tempfile.TemporaryDirectory() as work:
        folder = Path(work)
        source = folder / "csv"
        source.mkdir()
        with (source / "ProductOverview.csv").open("w", newline="") as overview, \
                (source / "DietarySupplementFacts.csv").open("w", newline="") as facts:
            products = csv.writer(overview)
            ingredients = csv.writer(facts)
            products.writerow(["DSLD ID", "Product Name", "Market Status", "Suggested Use"])
            ingredients.writerow(["DSLD ID", "Ingredient", "Amount Per Serving",
                                  "Amount Per Serving Unit", "Panel"])
            for label in range(1, labels + 1):
                matched = label % match_every == 0
                products.writerow([str(label), f"Synthetic {'creatine' if matched else 'other'} {label}",
                                   "On Market", "One serving daily"])
                for panel in range(facts_per_label):
                    ingredient = "Creatine Monohydrate" if matched and panel < 2 else "Synthetic other ingredient"
                    amount, unit = ("500", "mg") if panel == 0 else ("4", "g")
                    ingredients.writerow([str(label), ingredient, amount, unit, str(panel)])
        database = folder / "synthetic.db"
        start = perf_counter()
        load_snapshot(source, database)
        load_seconds = perf_counter() - start
        if unindexed:
            with sqlite3.connect(database) as con:
                con.execute('DROP INDEX product_id')
                con.execute('DROP INDEX ingredient_product_id')
        before = sha256(database)
        outputs = [folder / "first", folder / "second"]
        timings = []
        for output in outputs:
            start = perf_counter()
            metadata = analyze(database, output, "Synthetic scale fixture, not DSLD")
            timings.append(perf_counter() - start)
        expected = labels // match_every
        assert metadata["matched_ids"] == expected
        assert metadata["source_counts"]["ProductOverview"] == labels
        assert metadata["source_counts"]["DietarySupplementFacts"] == labels * facts_per_label
        assert sha256(database) == before
        for path in outputs[0].iterdir():
            assert sha256(path) == sha256(outputs[1] / path.name), path.name
        with (outputs[0] / "records.csv").open() as stream:
            records = list(csv.DictReader(stream))
        assert len(records) == expected
        assert all(float(row["min_grams"]) == .5 and float(row["max_grams"]) == 4
                   and int(row["matching_rows"]) == 2 for row in records)
        exported = 0
        with (outputs[0] / "source_labels.jsonl").open() as stream:
            for line in stream:
                label = json.loads(line)
                assert len(label["matched_facts"]) == 2
                assert len(label["other_facts"]) == facts_per_label - 2
                exported += 1
        assert exported == expected
        return dict(fixture="synthetic, not DSLD", labels=labels,
                    facts=labels * facts_per_label, matched_labels=expected,
                    source_indexes=not unindexed, database_bytes=database.stat().st_size,
                    load_seconds=round(load_seconds, 3),
                    analysis_seconds=[round(seconds, 3) for seconds in timings],
                    deterministic_exports=True, source_unchanged=True,
                    python_version=sys.version.split()[0], sqlite_version=sqlite3.sqlite_version)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=int, default=220000)
    parser.add_argument("--facts-per-label", type=int, default=10)
    parser.add_argument("--match-every", type=int, default=100)
    parser.add_argument("--unindexed", action="store_true")
    args = parser.parse_args()
    if args.labels < 1 or args.facts_per_label < 2 or not 1 <= args.match_every <= args.labels:
        parser.error("Use positive labels, at least two facts per label, and match-every between 1 and labels")
    print(json.dumps(benchmark(args.labels, args.facts_per_label,
                               args.match_every, args.unindexed), indent=2))


if __name__ == "__main__":
    main()
