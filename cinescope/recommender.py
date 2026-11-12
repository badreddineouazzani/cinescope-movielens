"""Classement du catalogue et recommandation par similarité de genres."""
import numpy as np
import pandas as pd


def cosine_similarity(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    normalized = np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms != 0)
    return normalized @ normalized.T


def popularity(ratings, min_votes=20):
    summary = ratings.groupby("movie_id")["rating"].agg(average="mean", votes="size")
    return summary.loc[summary["votes"] >= min_votes].sort_values(
        ["average", "votes"], ascending=False, kind="stable",
    )


class ContentModel:
    def __init__(self, movies):
        self.movie_ids = pd.Index(movies["movie_id"])
        tokens = movies["genres"].str.lower().str.get_dummies(sep=" ").to_numpy(dtype=float)
        inverse_frequency = np.log((len(movies) + 1) / (tokens.sum(axis=0) + 1)) + 1
        vectors = tokens * inverse_frequency
        self.similarity = np.round(cosine_similarity(vectors), 12)

    def rank(self, movie_id, excluded=()):
        index = self.movie_ids.get_loc(movie_id)
        scores = pd.Series(self.similarity[index], index=self.movie_ids, name="similarity")
        scores = scores.drop([movie_id, *excluded], errors="ignore")
        return scores.loc[scores > 0].sort_values(ascending=False, kind="stable")
