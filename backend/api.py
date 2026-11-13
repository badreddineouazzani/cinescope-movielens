"""CinéScope, plateforme FastAPI pour MovieLens 100K."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from big_data.storage import ROOT, load
from backend.recommendation_filters import RecommendationFilters
from backend.algorithm.knn import MovieKNN
from backend.popularity import popularity

WEB = ROOT / "frontend" / "dist"


class Catalog:
    def __init__(self):
        if os.getenv("CINESCOPE_SOURCE") == "official" or os.getenv("VERCEL") == "1":
            from big_data.cloud_source import load_official

            movies, self.ratings = load_official()
        else:
            movies, self.ratings = load()
        self.movies = movies.set_index("movie_id")
        self.filters = RecommendationFilters(self.movies)
        self.user_count = self.ratings["user_id"].nunique()
        self.summary = popularity(self.ratings, min_votes=1)
        self.recommender = MovieKNN(movies, self.summary)
        self.counts = self.ratings["rating"].value_counts().reindex(range(1, 6), fill_value=0)

    def records(self, ids):
        rows = []
        for movie_id in ids:
            movie = self.movies.loc[movie_id]
            stats = self.summary.loc[movie_id] if movie_id in self.summary.index else None
            row = {"id": int(movie_id), "title": movie.title,
                   "genres": movie.genres.split(),
                   "rating": round(float(stats.average), 2) if stats is not None else None,
                   "votes": int(stats.votes) if stats is not None else 0}
            rows.append(row)
        return rows


@asynccontextmanager
async def lifespan(app):
    app.state.catalog = Catalog()
    yield


app = FastAPI(title="CinéScope", description="Catalogue et recommandations MovieLens 100K",
              version="1.7.0", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=WEB / "assets", check_dir=False), name="assets")


@app.get("/", include_in_schema=False)
def index():
    page = WEB / "index.html"
    if not page.is_file():
        raise HTTPException(503, "Compilez le frontend avec npm --prefix frontend run build.")
    return FileResponse(page)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def stats(request: Request):
    catalog = request.app.state.catalog
    return {"movies": len(catalog.movies), "ratings": len(catalog.ratings),
            "users": catalog.user_count,
            "distribution": [{"rating": int(note), "count": int(count)}
                             for note, count in catalog.counts.items()],
            "most_rated": catalog.records(catalog.summary.nlargest(10, "votes").index)}


@app.get("/api/movies")
def movies(request: Request, q: str = Query("", max_length=120), limit: int = Query(12, ge=1, le=50)):
    catalog = request.app.state.catalog
    titles = catalog.movies["title"]
    matches = titles[titles.str.contains(q.strip(), case=False, regex=False)]
    return catalog.records(matches.sort_values().index[:limit])


@app.get("/api/popular")
def popular(request: Request, min_votes: int = Query(20, ge=1, le=1000),
            limit: int = Query(10, ge=1, le=50)):
    catalog = request.app.state.catalog
    top = catalog.summary.loc[catalog.summary["votes"] >= min_votes].head(limit)
    return catalog.records(top.index)


@app.get("/api/recommendation-filters")
def recommendation_filters(request: Request):
    catalog = request.app.state.catalog
    return catalog.filters.options()


@app.get("/api/recommendations")
def recommend(request: Request, movie_id: int = Query(ge=1),
              limit: int = Query(10, ge=1, le=50),
              genre: str | None = Query(None, max_length=32),
              decade: int | None = Query(None, ge=1800, le=2100, multiple_of=10)):
    catalog = request.app.state.catalog
    if movie_id not in catalog.movies.index:
        raise HTTPException(404, "Film introuvable.")
    if genre is not None and genre not in catalog.filters.genres:
        raise HTTPException(422, "Genre inconnu.")
    ranked_ids = catalog.recommender.rank(movie_id).index
    matches = catalog.filters.apply(ranked_ids, genre, decade)
    return {"movies": catalog.records(matches[:limit])}
