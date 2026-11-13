"""Spark ETL sur l’archive locale MovieLens 100K."""
import argparse
import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

from pyspark.sql import SparkSession

from big_data.cleaning import clean_movies, clean_ratings

from big_data.storage import DATA, GENRES, load

RATINGS = "user_id INT, movie_id INT, rating INT, timestamp LONG"
MOVIES = ("movie_id INT, title STRING, release STRING, video_release STRING, "
          "imdb_url STRING, " + ", ".join(f"{genre} INT" for genre in GENRES))
MEMBERS = ["u.data", "u.item", "u.user", "u1.base", "u1.test"]


def prepare(archive_path):
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    spark = (SparkSession.builder.master("local[2]").appName("CineScope MovieLens ETL")
             .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", 4)
             .config("spark.sql.session.timeZone", "UTC").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        with tempfile.TemporaryDirectory() as temp, ZipFile(archive_path) as archive:
            source = Path(temp)
            for member in MEMBERS:
                (source / member).write_bytes(archive.read(f"ml-100k/{member}"))
            # Spark's CSV source expects UTF-8. Convert the legacy catalog encoding explicitly.
            item = source / "u.item"
            item.write_text(item.read_text(encoding="latin-1"), encoding="utf-8")
            movies = clean_movies(spark.read.csv(str(item), sep="|", schema=MOVIES)).cache()
            users = (spark.read.csv(str(source / "u.user"), sep="|",
                                   schema="user_id INT, age INT, gender STRING, occupation STRING, zip STRING")
                     .select("user_id").dropna().dropDuplicates())
            movies.write.mode("overwrite").parquet(str(DATA / "movies"))
            for raw, target in [("u.data", "ratings"), ("u1.base", "train"), ("u1.test", "test")]:
                raw_ratings = spark.read.csv(str(source / raw), sep="\t", schema=RATINGS)
                ratings = clean_ratings(raw_ratings, users, movies.select("movie_id"))
                ratings.write.mode("overwrite").parquet(str(DATA / target))
            for target in ["movies", "ratings", "train", "test"]:
                print(f"{target}: {spark.read.parquet(str(DATA / target)).count():,}")
    finally:
        spark.stop()
    movies, ratings = load()
    movies.to_csv(DATA / "movies.csv", index=False)
    ratings.to_csv(DATA / "ratings.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Chemin vers ml-100k.zip")
    prepare(parser.parse_args().archive.expanduser().resolve())
