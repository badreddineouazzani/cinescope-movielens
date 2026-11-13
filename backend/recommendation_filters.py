"""Filtres de genre et de décennie appliqués aux suggestions classées."""

from big_data.storage import GENRES


class RecommendationFilters:
    def __init__(self, movies):
        self.movie_genres = movies["genres"].str.get_dummies(sep=" ").astype(bool)
        years = movies["title"].str.extract(r"\((\d{4})\)(?:\s+\([^)]+\))*$", expand=False)
        self.decades = years.astype("Int64") // 10 * 10
        self.genres = sorted(genre for genre in GENRES if genre != "unknown" and genre in self.movie_genres)

    def options(self):
        return {
            "genres": self.genres,
            "decades": sorted(self.decades.dropna().unique().tolist(), reverse=True),
        }

    def apply(self, ranked_ids, genre, decade):
        if genre is not None:
            ranked_ids = ranked_ids[self.movie_genres.loc[ranked_ids, genre].to_numpy()]
        if decade is not None:
            matches = self.decades.loc[ranked_ids].eq(decade).fillna(False)
            ranked_ids = ranked_ids[matches.to_numpy(dtype=bool)]
        return ranked_ids
