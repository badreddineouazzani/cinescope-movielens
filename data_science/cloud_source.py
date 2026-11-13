"""Chargement du catalogue et des notes depuis l’archive officielle GroupLens."""

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

from data_science.archive import read_archive

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"


def load_official():
    with urlopen(MOVIELENS_URL, timeout=20) as response:
        archive_bytes = response.read(6_000_000)
    with ZipFile(BytesIO(archive_bytes)) as archive:
        tables = read_archive(archive)
    return tables["movies"], tables["ratings"]
