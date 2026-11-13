"""Lecture et nettoyage des tables brutes de l’archive MovieLens 100K."""

from csv import QUOTE_NONE

import pandas as pd

from data_science.cleaning import clean_movies, clean_ratings
from data_science.storage import GENRES

RATING_COLUMNS = ["user_id", "movie_id", "rating", "timestamp"]
MOVIE_COLUMNS = ["movie_id", "title", "release", "video", "imdb", *GENRES]


def read_archive(archive, *, include_split=False):
    with archive.open("ml-100k/u.item") as source:
        movies = clean_movies(pd.read_csv(
            source, sep="|", encoding="latin-1", names=MOVIE_COLUMNS,
            keep_default_na=False, na_values=[""], quoting=QUOTE_NONE,
        ))
    with archive.open("ml-100k/u.user") as source:
        users = pd.read_csv(source, sep="|", names=["user_id"], usecols=[0])["user_id"]

    members = {"ratings": "u.data"}
    if include_split:
        members.update(train="u1.base", test="u1.test")

    tables = {"movies": movies}
    for table, member in members.items():
        with archive.open(f"ml-100k/{member}") as source:
            ratings = pd.read_csv(source, sep="\t", names=RATING_COLUMNS)
        tables[table] = clean_ratings(ratings, users, movies)
    return tables
