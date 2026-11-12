"""Chargement depuis GroupLens sur une instance sans artefacts Spark locaux."""
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd

from cinescope.data import GENRES

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"


def load_official():
    with urlopen(MOVIELENS_URL, timeout=20) as response:
        archive_bytes = response.read(6_000_000)
    with ZipFile(BytesIO(archive_bytes)) as archive:
        with archive.open("ml-100k/u.item") as source:
            movies = pd.read_csv(source, sep="|", encoding="latin-1",
                                 names=["movie_id", "title", "release", "video",
                                        "imdb", *GENRES])
        with archive.open("ml-100k/u.data") as source:
            ratings = pd.read_csv(source, sep="\t",
                                  names=["user_id", "movie_id", "rating", "timestamp"])
        with archive.open("ml-100k/u.user") as source:
            users = pd.read_csv(source, sep="|", usecols=[0], header=None).iloc[:, 0]
    movies = movies.dropna(subset=["movie_id", "title"]).drop_duplicates("movie_id")
    movies["title"] = movies["title"].str.strip()
    movies["genres"] = movies[GENRES].apply(
        lambda row: " ".join(genre for genre in GENRES if row[genre] == 1), axis=1
    )
    ratings = (ratings.dropna().loc[lambda row: row["rating"].between(1, 5)]
               .sort_values("timestamp").drop_duplicates(["user_id", "movie_id"], keep="last"))
    ratings = ratings.loc[ratings["movie_id"].isin(movies["movie_id"]) &
                          ratings["user_id"].isin(users)].copy()
    ratings["rated_at"] = pd.to_datetime(ratings.pop("timestamp"), unit="s", utc=True)
    return movies[["movie_id", "title", "genres"]].sort_values("movie_id"), ratings
