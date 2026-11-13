"""K plus proches voisins entre films selon la distance de Jaccard."""
import numpy as np
import pandas as pd


class MovieKNN:
    def __init__(self, movies):
        self.movie_ids = pd.Index(movies["movie_id"])
        genres = movies["genres"].str.get_dummies(sep=" ").drop(columns="unknown", errors="ignore")
        self.genre_vectors = genres.to_numpy(dtype=bool)
        self.genre_counts = np.count_nonzero(self.genre_vectors, axis=1)

    def rank(self, movie_id, excluded=()):
        position = self.movie_ids.get_loc(movie_id)
        shared = np.count_nonzero(self.genre_vectors & self.genre_vectors[position], axis=1)
        union = self.genre_counts + self.genre_counts[position] - shared

        # Un film sans genre commun ne fait pas partie des voisins recommandables.
        candidates = shared > 0
        distances = 1 - shared[candidates] / union[candidates]
        neighbors = pd.Series(distances, index=self.movie_ids[candidates], name="distance")
        neighbors = neighbors.drop([movie_id, *excluded], errors="ignore")
        return neighbors.sort_values(kind="stable")
