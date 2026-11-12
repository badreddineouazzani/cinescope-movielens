"""Chargement du catalogue et des évaluations préparés par Spark."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GENRES = [
    "unknown", "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film_Noir", "Horror",
    "Musical", "Mystery", "Romance", "Sci_Fi", "Thriller", "War", "Western",
]


def load():
    movies = pd.read_parquet(DATA / "movies").sort_values("movie_id", ignore_index=True)
    ratings = pd.read_parquet(DATA / "ratings")
    return movies, ratings


def read_split():
    return pd.read_parquet(DATA / "train"), pd.read_parquet(DATA / "test")
