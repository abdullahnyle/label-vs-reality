"""Load one extracted DSLD CSV snapshot into a new SQLite database."""

import argparse
import csv
import hashlib
import json
import sqlite3
import tempfile
from datetime import date
from pathlib import Path

TABLES = ("ProductOverview", "DietarySupplementFacts")


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(folder):
    files = {
        table: sorted(
            path for path in folder.rglob("*.csv")
            if path.stem == table or path.stem.startswith(table + "_")
        )
        for table in TABLES
    }
    for table, paths in files.items():
        if not paths:
            raise ValueError(f"No {table} CSV files found in {folder}")
    return files


def load_snapshot(source, destination, acquired_on=None):
    if destination.exists():
        raise ValueError(f"Output already exists: {destination}")
    if acquired_on is not None:
        date.fromisoformat(acquired_on)

    files = source_files(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        temporary = Path(work) / "snapshot.db"
        connection = sqlite3.connect(temporary)
        try:
            connection.execute(
                "CREATE TABLE ImportManifest "
                "(table_name TEXT, file_name TEXT, sha256 TEXT, rows INTEGER, acquired_on TEXT)"
            )
            for table, paths in files.items():
                expected_headers = None
                for path in paths:
                    before = sha256(path)
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.reader(stream, strict=True)
                        headers = next(reader, None)
                        if not headers or len(set(headers)) != len(headers) or any(not h for h in headers):
                            raise ValueError(f"Invalid header: {path.name}")
                        if expected_headers is None:
                            expected_headers = headers
                            columns = ", ".join(quote(header) + " TEXT" for header in headers)
                            connection.execute(f"CREATE TABLE {quote(table)} ({columns})")
                        elif headers != expected_headers:
                            raise ValueError(f"Header differs between batches: {path.name}")

                        placeholders = ",".join("?" for _ in headers)
                        insert = f"INSERT INTO {quote(table)} VALUES ({placeholders})"
                        count = 0
                        for row in reader:
                            if len(row) != len(headers):
                                raise ValueError(
                                    f"Wrong field count in {path.name}, CSV line {reader.line_num}"
                                )
                            connection.execute(insert, row)
                            count += 1
                    if before != sha256(path):
                        raise ValueError(f"Source changed during import: {path.name}")
                    connection.execute(
                        "INSERT INTO ImportManifest VALUES (?,?,?,?,?)",
                        (table, path.relative_to(source).as_posix(), before, count, acquired_on),
                    )

                blank_ids = connection.execute(
                    f"SELECT COUNT(*) FROM {quote(table)} "
                    "WHERE [DSLD ID] IS NULL OR trim([DSLD ID]) = ''"
                ).fetchone()[0]
                if blank_ids:
                    raise ValueError(f"{table} has {blank_ids} blank IDs")

            connection.execute("CREATE UNIQUE INDEX product_id ON ProductOverview ([DSLD ID])")
            connection.execute(
                "CREATE INDEX ingredient_product_id ON DietarySupplementFacts ([DSLD ID])"
            )
            orphaned_facts = connection.execute(
                "SELECT COUNT(*) FROM DietarySupplementFacts AS facts "
                "LEFT JOIN ProductOverview AS products "
                "ON products.[DSLD ID] = facts.[DSLD ID] "
                "WHERE products.[DSLD ID] IS NULL"
            ).fetchone()[0]
            if orphaned_facts:
                raise ValueError(
                    f"DietarySupplementFacts has {orphaned_facts} rows without a product record"
                )
            connection.commit()
        finally:
            connection.close()

        # A hard link fails if another process created the destination mid-import.
        destination.hardlink_to(temporary)
    return {"database": str(destination), "sha256": sha256(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--acquired-on", help="Known acquisition date in YYYY-MM-DD format")
    args = parser.parse_args()
    try:
        print(json.dumps(load_snapshot(args.source, args.destination, args.acquired_on), indent=2))
    except (ValueError, csv.Error, sqlite3.Error, OSError) as error:
        parser.exit(1, f"Import failed: {error}\n")


if __name__ == "__main__":
    main()
