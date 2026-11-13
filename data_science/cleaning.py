"""Nettoyage du catalogue et des notes MovieLens avec Pandas."""

import pandas as pd

from data_science.storage import GENRES


def clean_movies(movies):
    movies = movies.dropna(subset=["movie_id", "title"]).copy()
    movies["title"] = movies["title"].str.strip()
    movies = movies.loc[movies["title"].ne("")].drop_duplicates("movie_id").copy()
    movies["genres"] = movies[GENRES].apply(
        lambda row: " ".join(genre for genre in GENRES if row[genre] == 1), axis=1
    )
    return movies[["movie_id", "title", "genres"]].sort_values("movie_id", ignore_index=True)


def clean_ratings(ratings, users, movies):
    ratings = ratings.dropna()
    ratings = ratings.loc[
        ratings["rating"].between(1, 5)
        & ratings["movie_id"].isin(movies["movie_id"])
        & ratings["user_id"].isin(users)
    ]
    ratings = (
        ratings.sort_values("timestamp", kind="stable")
        .drop_duplicates(["user_id", "movie_id"], keep="last")
        .copy()
    )
    ratings["rated_at"] = pd.to_datetime(ratings.pop("timestamp"), unit="s", utc=True)
    return ratings.reset_index(drop=True)
