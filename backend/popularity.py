"""Classement du catalogue par moyenne des notes et nombre de votes."""


def popularity(ratings, min_votes=20):
    summary = ratings.groupby("movie_id")["rating"].agg(average="mean", votes="size")
    return summary.loc[summary["votes"] >= min_votes].sort_values(
        ["average", "votes"], ascending=False, kind="stable",
    )
