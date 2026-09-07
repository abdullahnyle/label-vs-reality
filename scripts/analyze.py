"""Screen recorded creatine amounts in a local DSLD snapshot."""

import argparse
import csv
import html
import json
import random
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

from amounts import parse_amount
from load_data import quote, sha256

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "ProductOverview": {"DSLD ID", "Product Name", "Market Status", "Suggested Use"},
    "DietarySupplementFacts": {"DSLD ID", "Ingredient", "Amount Per Serving", "Amount Per Serving Unit"},
}


def rows(con, query, params=()):
    return [dict(row) for row in con.execute(query, params)]


def check_source(con):
    counts = {}
    for table, required in REQUIRED.items():
        columns = {row[1] for row in con.execute(f"PRAGMA table_info({quote(table)})")}
        if required - columns:
            raise ValueError(f"{table} is missing columns: {', '.join(sorted(required - columns))}")
        counts[table] = con.execute(f"SELECT COUNT(*) FROM {quote(table)}").fetchone()[0]
        blank = con.execute(f"SELECT COUNT(*) FROM {quote(table)} WHERE [DSLD ID] IS NULL OR trim([DSLD ID]) = ''").fetchone()[0]
        if blank:
            raise ValueError(f"{table} has {blank} blank IDs")
    duplicate = con.execute('SELECT [DSLD ID] FROM ProductOverview GROUP BY [DSLD ID] HAVING COUNT(*) > 1 LIMIT 1').fetchone()
    if duplicate:
        raise ValueError(f"Duplicate ProductOverview ID: {duplicate[0]}")
    orphan = con.execute('SELECT COUNT(*) FROM DietarySupplementFacts f LEFT JOIN ProductOverview p ON f.[DSLD ID] = p.[DSLD ID] WHERE p.[DSLD ID] IS NULL').fetchone()[0]
    if orphan:
        raise ValueError(f"{orphan} ingredient rows have no ProductOverview record")
    counts["orphan_ingredient_rows"] = orphan
    return counts


def setup(con):
    con.create_function("amount_status", 2, lambda a, u: parse_amount(a, u)[1], deterministic=True)
    con.create_function("amount_grams", 2, lambda a, u: parse_amount(a, u)[0], deterministic=True)
    con.execute('CREATE TEMP TABLE CreatineAliases (ingredient TEXT PRIMARY KEY, explicit_monohydrate INTEGER CHECK (explicit_monohydrate IN (0,1)))')
    with (ROOT / "config/creatine_aliases.csv").open(newline="", encoding="utf-8") as stream:
        aliases = [(row["ingredient"], int(row["explicit_monohydrate"])) for row in csv.DictReader(stream)]
    con.executemany('INSERT INTO CreatineAliases VALUES (?,?)', aliases)
    con.execute('CREATE TEMP TABLE AnalysisOptions (expanded INTEGER NOT NULL)')
    con.execute('INSERT INTO AnalysisOptions VALUES (1)')
    con.executescript((ROOT / "sql/03_creatine_reference.sql").read_text())


def build_analysis(con, expanded=True):
    con.execute('UPDATE AnalysisOptions SET expanded = ?', (int(expanded),))
    con.executescript((ROOT / "sql/04_creatine_analysis.sql").read_text())
    expected = con.execute('SELECT COUNT(DISTINCT dsld_id) FROM CreatineRows').fetchone()[0]
    actual = con.execute('SELECT COUNT(*), COUNT(DISTINCT dsld_id) FROM CreatineRecords').fetchone()
    if tuple(actual) != (expected, expected):
        raise ValueError("The join changed the number of matched label IDs")
    return rows(con, 'SELECT * FROM CreatineRecords ORDER BY dsld_id')


def write_csv(path, records, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sensitivity(records, alias_policy):
    result = []
    for population in ("all", "on_market", "off_market", "unknown"):
        selected = [r for r in records if population == "all" or r["market_status"] == population]
        for selection in ("max", "min"):
            for threshold in (2.5, 3.0, 5.0):
                amounts = [r[f"{selection}_grams"] for r in selected if r[f"{selection}_grams"] is not None]
                above = sum(value >= threshold for value in amounts)
                result.append(dict(alias_policy=alias_policy, population=population,
                                   selection=selection, threshold_g=threshold,
                                   total=len(selected), usable=len(amounts),
                                   at_least_threshold=above, below_threshold=len(amounts)-above,
                                   unusable=len(selected)-len(amounts),
                                   percent_of_usable=round(100*above/len(amounts), 4) if amounts else None))
    return result


def export_evidence(con, destination, records):
    write_csv(destination / "records.csv", records,
              [d[0] for d in con.execute('SELECT * FROM CreatineRecords LIMIT 0').description])
    matched = rows(con, 'SELECT * FROM CreatineRows ORDER BY dsld_id, source_rowid')
    write_csv(destination / "matched_rows.csv", matched,
              [d[0] for d in con.execute('SELECT * FROM CreatineRows LIMIT 0').description])
    units = rows(con, 'SELECT raw_unit, parse_status, COUNT(*) AS rows FROM CreatineRows GROUP BY raw_unit, parse_status ORDER BY raw_unit, parse_status')
    write_csv(destination / "parsing.csv", units, ["raw_unit", "parse_status", "rows"])
    unmatched = rows(con, "SELECT f.Ingredient AS ingredient, COUNT(*) AS rows FROM DietarySupplementFacts f LEFT JOIN CreatineAliases a ON f.Ingredient = a.ingredient WHERE lower(f.Ingredient) LIKE '%creatin%' AND a.ingredient IS NULL GROUP BY f.Ingredient ORDER BY f.Ingredient")
    write_csv(destination / "unmatched_names.csv", unmatched, ["ingredient", "rows"])

    # Read overview metadata once; older DB Browser imports may lack an ID index.
    labels = {}
    query = 'SELECT c.dsld_id AS analysis_id, p.* FROM ProductOverview p JOIN CreatineRecords c ON p.[DSLD ID] = c.dsld_id'
    for label in rows(con, query):
        labels[label.pop("analysis_id")] = label

    # Preserve the full source fields; panel metadata differs between exports.
    with (destination / "source_labels.jsonl").open("w", encoding="utf-8") as stream:
        for record in records:
            label = labels[record["dsld_id"]]
            facts = rows(con, 'SELECT f.rowid AS source_rowid, f.* FROM DietarySupplementFacts f JOIN CreatineRows c ON f.rowid = c.source_rowid WHERE c.dsld_id = ? ORDER BY f.rowid', (record["dsld_id"],))
            stream.write(json.dumps({"label": label, "matched_facts": facts}, ensure_ascii=False) + "\n")

    candidates = []
    for record in records:
        if record["market_status"] == "on_market" and record["threshold_category"] == "below_3g" and record["name_group"] == "name_contains_creatine":
            candidates.append(dict(record, label_url=f'https://dsld.od.nih.gov/label/{record["dsld_id"]}',
                                   review_status="pending", dosage_form="", serving_basis="",
                                   daily_min_g="", daily_max_g="", reviewer="", reviewed_on="", notes=""))
    fields = ["dsld_id", "label_url", "product_name", "max_grams", "selected_source_rowid", "unresolved_rows", "suggested_use", "review_status", "dosage_form", "serving_basis", "daily_min_g", "daily_max_g", "reviewer", "reviewed_on", "notes"]
    write_csv(destination / "candidate_review_queue.csv", candidates, fields)
    pool = [r for r in records if r["market_status"] == "on_market" and (r["suggested_use"] or "").strip()]
    sample = random.Random(20260907).sample(pool, min(30, len(pool)))
    sample = [dict(r, review_status="pending", direction_type="", notes="") for r in sample]
    write_csv(destination / "suggested_use_sample.csv", sample,
              ["dsld_id", "product_name", "suggested_use", "review_status", "direction_type", "notes"])
    return len(candidates)


def write_report(destination, records, dataset_label):
    selected = [r for r in records if r["market_status"] == "on_market"]
    counts = Counter(r["threshold_category"] for r in selected)
    categories = ["at_least_3g", "below_3g", "unusable"]
    usable = counts["at_least_3g"] + counts["below_3g"]
    rate = f'{100 * counts["at_least_3g"] / usable:.1f}%' if usable else "undefined (no usable amounts)"
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="260" viewBox="0 0 760 260">',
           '<rect width="760" height="260" fill="white"/>',
           f'<text x="20" y="30" font-family="sans-serif" font-size="18">{html.escape(dataset_label)}: on-market label records</text>']
    for index, category in enumerate(categories):
        y = 75 + index * 55
        width = 400 * counts[category] / max(len(selected), 1)
        svg.extend([f'<text x="20" y="{y+20}" font-family="sans-serif" font-size="15">{category}</text>',
                    f'<rect x="170" y="{y}" width="{width:.2f}" height="30" fill="{["#266b80", "#b27332", "#80858c"][index]}"/>',
                    f'<text x="{185+width:.2f}" y="{y+20}" font-family="sans-serif" font-size="15">{counts[category]}</text>'])
    svg.append('</svg>')
    (destination / "amounts.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
    lines = ["# Recorded creatine amounts", "", f"Dataset: {dataset_label}", "",
             "Unit: distinct DSLD label ID. Selection: maximum usable recorded amount per serving.", "",
             "| Group | Records |", "|---|---:|"]
    lines += [f"| {category} | {counts[category]} |" for category in categories]
    lines += ["", f"At least 3 g among usable records: {rate}. Total on-market records: {len(selected)}.", "",
              "![Recorded amounts](amounts.svg)", "",
              "These are automated label-amount classifications. Source-panel validation and manual candidate review remain separate steps. Daily intake, actual contents and effectiveness were not assessed.", "",
              "See sensitivity.csv for alternative thresholds, serving selections, market populations and explicit-monohydrate aliases. See run.json for provenance.", ""]
    (destination / "report.md").write_text("\n".join(lines), encoding="utf-8")


def analyze(database, output, dataset_label):
    if not database.is_file():
        raise ValueError(f"Database not found: {database}")
    if output.exists():
        raise ValueError(f"Output already exists: {output}; choose a new run directory")
    for suffix in ("-wal", "-journal"):
        companion = Path(str(database) + suffix)
        if companion.exists() and companion.stat().st_size:
            raise ValueError("Close the database writer and checkpoint/save it before analysis")
    fingerprint = sha256(database)
    con = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_counts = check_source(con)
        setup(con)
        with tempfile.TemporaryDirectory(dir=output.parent) as work:
            destination = Path(work) / "run"
            destination.mkdir()
            expanded = build_analysis(con)
            candidates = export_evidence(con, destination, expanded)
            summary = sensitivity(expanded, "expanded")
            explicit = build_analysis(con, expanded=False)
            summary += sensitivity(explicit, "explicit_monohydrate")
            write_csv(destination / "sensitivity.csv", summary, list(summary[0]))
            write_report(destination, expanded, dataset_label)
            tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            metadata = dict(dataset_label=dataset_label, database_sha256=fingerprint,
                            source_counts=source_counts, matched_ids=len(expanded),
                            candidate_reviews_pending=candidates, sample_seed=20260907,
                            python_version=sys.version.split()[0], sqlite_version=sqlite3.sqlite_version,
                            source_manifest=rows(con, 'SELECT * FROM ImportManifest ORDER BY table_name, file_name') if "ImportManifest" in tables else None,
                            market_statuses=rows(con, 'SELECT [Market Status] AS status, COUNT(*) AS records FROM ProductOverview GROUP BY [Market Status] ORDER BY [Market Status]'),
                            code_sha256={p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted([*ROOT.glob("scripts/*.py"), *ROOT.glob("config/*.csv"), *ROOT.glob("sql/0[34]*.sql")])})
            if fingerprint != sha256(database):
                raise ValueError("Database changed during analysis; outputs were discarded")
            (destination / "run.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            destination.rename(output)
    finally:
        con.close()
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dataset-label", required=True, help="Snapshot name; label synthetic fixtures explicitly")
    args = parser.parse_args()
    try:
        metadata = analyze(args.database, args.output, args.dataset_label)
    except (ValueError, sqlite3.Error, OSError) as error:
        parser.exit(1, f"Analysis failed: {error}\n")
    print(f'Analyzed {metadata["matched_ids"]} label IDs. Results: {args.output}')


if __name__ == "__main__":
    main()
