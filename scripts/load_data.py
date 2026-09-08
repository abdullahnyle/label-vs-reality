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


def load_snapshot(source, destination, acquired_on=None):
    if destination.exists():
        raise ValueError(f"Output already exists: {destination}")
    if acquired_on is not None:
        date.fromisoformat(acquired_on)
    files = {
        table: sorted(p for p in source.rglob("*.csv")
                      if p.stem == table or p.stem.startswith(table + "_"))
        for table in TABLES
    }
    for table, paths in files.items():
        if not paths:
            raise ValueError(f"No {table} CSV files found in {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        temporary = Path(work) / "snapshot.db"
        con = sqlite3.connect(temporary)
        try:
            con.execute('CREATE TABLE ImportManifest (table_name TEXT, file_name TEXT, sha256 TEXT, rows INTEGER, acquired_on TEXT)')
            for table, paths in files.items():
                expected = None
                for path in paths:
                    before = sha256(path)
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.reader(stream, strict=True)
                        headers = next(reader, None)
                        if not headers or len(set(headers)) != len(headers) or any(not h for h in headers):
                            raise ValueError(f"Invalid header: {path.name}")
                        if expected is None:
                            expected = headers
                            columns = ", ".join(quote(h) + " TEXT" for h in headers)
                            con.execute(f"CREATE TABLE {quote(table)} ({columns})")
                        elif headers != expected:
                            raise ValueError(f"Header differs between batches: {path.name}")
                        statement = f"INSERT INTO {quote(table)} VALUES ({','.join('?' for _ in headers)})"
                        count = 0
                        for row in reader:
                            if len(row) != len(headers):
                                raise ValueError(f"Wrong field count in {path.name}, CSV line {reader.line_num}")
                            con.execute(statement, row)
                            count += 1
                    if before != sha256(path):
                        raise ValueError(f"Source changed during import: {path.name}")
                    con.execute("INSERT INTO ImportManifest VALUES (?,?,?,?,?)",
                                (table, path.relative_to(source).as_posix(), before, count, acquired_on))
                missing = con.execute(f'SELECT COUNT(*) FROM {quote(table)} WHERE [DSLD ID] IS NULL OR trim([DSLD ID]) = \'\'').fetchone()[0]
                if missing:
                    raise ValueError(f"{table} has {missing} blank IDs")
            con.execute('CREATE UNIQUE INDEX product_id ON ProductOverview ([DSLD ID])')
            con.execute('CREATE INDEX ingredient_product_id ON DietarySupplementFacts ([DSLD ID])')
            con.commit()
        finally:
            con.close()
        # Unlike rename, linking cannot replace a file created during the import.
        destination.hardlink_to(temporary)
    return {"database": str(destination), "sha256": sha256(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Extracted CSV folder")
    parser.add_argument("destination", type=Path, help="New database path")
    parser.add_argument("--acquired-on", help="Known acquisition date (YYYY-MM-DD); omit if unknown")
    args = parser.parse_args()
    try:
        print(json.dumps(load_snapshot(args.source, args.destination, args.acquired_on), indent=2))
    except (ValueError, csv.Error, sqlite3.Error, OSError) as error:
        parser.exit(1, f"Import failed: {error}\n")


if __name__ == "__main__":
    main()
