"""K plus proches voisins selon les genres, l’année, la note et les votes."""
import numpy as np
import pandas as pd

from big_data.storage import release_years


class MovieKNN:
    def __init__(self, movies, rating_summary):
        self.movie_ids = pd.Index(movies["movie_id"])
        genres = movies["genres"].str.get_dummies(sep=" ").drop(columns="unknown", errors="ignore")
        self.genre_vectors = genres.to_numpy(dtype=bool)
        self.genre_counts = np.count_nonzero(self.genre_vectors, axis=1)

        self.years = release_years(movies["title"]).to_numpy(dtype=float, na_value=np.nan)
        summary = rating_summary.reindex(self.movie_ids)
        self.average = summary["average"].to_numpy(dtype=float)
        self.log_votes = np.log1p(summary["votes"].fillna(0).to_numpy(dtype=float))
        self.vote_scale = max(self.log_votes.max(initial=0), 1.0)

    @staticmethod
    def _difference(values, position, scale):
        distance = np.abs(values - values[position]) / scale
        return np.nan_to_num(np.minimum(distance, 1.0), nan=0.5)

    def rank(self, movie_id, excluded=()):
        position = self.movie_ids.get_loc(movie_id)
        shared = np.count_nonzero(self.genre_vectors & self.genre_vectors[position], axis=1)
        union = self.genre_counts + self.genre_counts[position] - shared

        # Un film sans genre commun ne fait pas partie des voisins recommandables.
        candidates = shared > 0
        genre_distance = 1 - shared[candidates] / union[candidates]
        year_distance = self._difference(self.years, position, 30)
        rating_distance = self._difference(self.average, position, 4)
        vote_distance = self._difference(self.log_votes, position, self.vote_scale)
        distances = (
            0.60 * genre_distance
            + 0.15 * year_distance[candidates]
            + 0.15 * rating_distance[candidates]
            + 0.10 * vote_distance[candidates]
        )
        neighbors = pd.Series(distances, index=self.movie_ids[candidates], name="distance")
        neighbors = neighbors.drop([movie_id, *excluded], errors="ignore")
        return neighbors.sort_values(kind="stable")
