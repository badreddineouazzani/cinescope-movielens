"""Chargement du catalogue et des évaluations préparés en CSV."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GENRES = [
    "unknown", "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film_Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci_Fi", "Thriller", "War", "Western",
]


def release_years(titles):
    years = titles.str.extract(r"\((\d{4})\)(?:\s+\([^)]+\))*$", expand=False)
    return years.astype("Int64")


def _read_ratings(name):
    return pd.read_csv(DATA / f"{name}.csv", parse_dates=["rated_at"])


def load():
    movies = pd.read_csv(DATA / "movies.csv", keep_default_na=False)
    return movies.sort_values("movie_id", ignore_index=True), _read_ratings("ratings")


def read_split():
    return _read_ratings("train"), _read_ratings("test")
