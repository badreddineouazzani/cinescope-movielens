"""Classement de référence, TF-IDF par genre et k-NN utilisateur-utilisateur."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def popularity(ratings, min_votes=20):
    summary = ratings.groupby("movie_id")["rating"].agg(average="mean", votes="size")
    return summary.loc[summary["votes"] >= min_votes].sort_values(
        ["average", "votes"], ascending=False, kind="stable",
    )


class ContentModel:
    def __init__(self, movies):
        self.movie_ids = pd.Index(movies["movie_id"])
        vectors = TfidfVectorizer().fit_transform(movies["genres"])
        self.similarity = cosine_similarity(vectors)

    def rank(self, movie_id, excluded=()):
        index = self.movie_ids.get_loc(movie_id)
        scores = pd.Series(self.similarity[index], index=self.movie_ids, name="similarity")
        scores = scores.drop([movie_id, *excluded], errors="ignore")
        return scores.loc[scores > 0].sort_values(ascending=False, kind="stable")


class UserKNN:
    """Moyenne centrée pondérée sur les k utilisateurs les plus similaires."""

    def __init__(self, ratings, movie_ids, k=30):
        matrix = ratings.pivot(index="user_id", columns="movie_id", values="rating")
        matrix = matrix.reindex(columns=movie_ids)
        self.users = matrix.index
        self.movies = matrix.columns
        self.values = matrix.to_numpy()
        self.observed = ~np.isnan(self.values)
        self.user_means = np.nanmean(self.values, axis=1)
        self.centered = np.where(self.observed, self.values - self.user_means[:, None], 0)
        self.similarity = cosine_similarity(self.centered)
        np.fill_diagonal(self.similarity, 0)
        self.reference = ratings.groupby("movie_id")["rating"].mean().reindex(self.movies)
        self.reference = self.reference.fillna(ratings["rating"].mean()).rename("prediction")
        self.k = k

    def predict(self, user_id):
        if user_id not in self.users:
            return self.reference.copy()
        i = self.users.get_loc(user_id)
        similarities = self.similarity[i]
        neighbors = np.argsort(-similarities, kind="stable")[:self.k]
        neighbors = neighbors[similarities[neighbors] > 0]
        weights = similarities[neighbors]
        numerator = weights @ self.centered[neighbors]
        denominator = weights @ self.observed[neighbors]
        prediction = self.reference.to_numpy(copy=True)
        np.divide(numerator, denominator, out=numerator, where=denominator > 0)
        usable = denominator > 0
        prediction[usable] = self.user_means[i] + numerator[usable]
        return pd.Series(np.clip(prediction, 1, 5), index=self.movies, name="prediction")

    def seen(self, user_id):
        return self.movies[self.observed[self.users.get_loc(user_id)]]

    def rank(self, user_id):
        return self.predict(user_id).drop(self.seen(user_id)).sort_values(
            ascending=False, kind="stable",
        )


def hybrid_rank(content, collaborative, rank_constant=60):
    def rank_score(ranking):
        return pd.Series(1 / (rank_constant + np.arange(1, len(ranking) + 1)), index=ranking.index)

    scores = rank_score(content).add(rank_score(collaborative), fill_value=0)
    return scores.sort_values(ascending=False, kind="stable").rename("hybrid_score")
