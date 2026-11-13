"""Prépare les fichiers CSV MovieLens 100K à partir de l’archive locale."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from data_science.archive import read_archive
from data_science.storage import DATA


def prepare(archive_path):
    with ZipFile(archive_path) as archive:
        tables = read_archive(archive, include_split=True)

    DATA.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=DATA) as staging:
        for name, table in tables.items():
            table.to_csv(Path(staging) / f"{name}.csv", index=False)
        for name, table in tables.items():
            filename = f"{name}.csv"
            (Path(staging) / filename).replace(DATA / filename)
            print(f"{name}: {len(table):,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Chemin vers ml-100k.zip")
    prepare(parser.parse_args().archive.expanduser().resolve())
