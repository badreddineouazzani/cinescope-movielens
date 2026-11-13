"""Nettoyage du catalogue et des notes avec PySpark."""

from pyspark.sql import Window, functions as F

from data_science.storage import GENRES


def clean_movies(movies):
    genres = F.concat_ws(" ", *[F.when(F.col(genre) == 1, F.lit(genre)) for genre in GENRES])
    return (
        movies.dropna(subset=["movie_id", "title"])
        .dropDuplicates(["movie_id"])
        .select("movie_id", F.trim("title").alias("title"), genres.alias("genres"))
    )


def clean_ratings(ratings, users, movies):
    latest = Window.partitionBy("user_id", "movie_id").orderBy(F.desc("timestamp"))
    return (
        ratings.dropna()
        .where(F.col("rating").between(1, 5))
        .withColumn("row", F.row_number().over(latest))
        .where("row = 1")
        .join(users, "user_id", "left_semi")
        .join(movies, "movie_id", "left_semi")
        .select("user_id", "movie_id", "rating", F.timestamp_seconds("timestamp").alias("rated_at"))
    )
