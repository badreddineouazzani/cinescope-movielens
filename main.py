"""CinéScope, plateforme FastAPI pour MovieLens 100K."""
import os
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

from cinescope.data import ROOT, load
from cinescope.recommender import ContentModel, UserKNN, hybrid_rank, popularity

WEB = ROOT / "frontend"
Mode = Literal["content", "collaborative", "hybrid"]


class Catalog:
    def __init__(self):
        if os.getenv("CINESCOPE_SOURCE") == "official" or os.getenv("VERCEL") == "1":
            from cinescope.cloud_data import load_official

            movies, self.ratings = load_official()
        else:
            movies, self.ratings = load()
        self.movies = movies.set_index("movie_id")
        self.content = ContentModel(movies)
        self.knn = UserKNN(self.ratings, movies["movie_id"])
        self.summary = popularity(self.ratings, min_votes=1)
        self.counts = self.ratings["rating"].value_counts().reindex(range(1, 6), fill_value=0)
        self.results = {}
        for key, filename in [("ratings", "metriques_notes.csv"), ("ranking", "metriques_classement.csv")]:
            file = ROOT / "artifacts" / filename
            self.results[key] = pd.read_csv(file).round(6).to_dict("records") if file.exists() else []

    def records(self, ids, scores=None):
        rows = []
        for movie_id in ids:
            movie = self.movies.loc[movie_id]
            stats = self.summary.loc[movie_id] if movie_id in self.summary.index else None
            row = {"id": int(movie_id), "title": movie.title,
                   "genres": movie.genres.split(),
                   "rating": round(float(stats.average), 2) if stats is not None else None,
                   "votes": int(stats.votes) if stats is not None else 0}
            if scores is not None:
                row["score"] = round(float(scores.loc[movie_id]), 5)
            rows.append(row)
        return rows


@asynccontextmanager
async def lifespan(app):
    app.state.catalog = Catalog()
    yield


app = FastAPI(title="CinéScope", description="Catalogue et recommandations MovieLens 100K",
              version="1.0.0", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=WEB), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def stats(request: Request):
    catalog = request.app.state.catalog
    return {"movies": len(catalog.movies), "ratings": len(catalog.ratings),
            "users": len(catalog.knn.users),
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


@app.get("/api/recommendations")
def recommend(request: Request, mode: Mode, movie_id: int | None = Query(None, ge=1),
              user_id: int | None = Query(None, ge=1), limit: int = Query(10, ge=1, le=50)):
    catalog = request.app.state.catalog
    if mode in {"content", "hybrid"}:
        if movie_id is None:
            raise HTTPException(422, "Choisissez un film.")
        if movie_id not in catalog.movies.index:
            raise HTTPException(404, "Film introuvable.")
    if mode in {"collaborative", "hybrid"}:
        if user_id is None:
            raise HTTPException(422, "Choisissez un profil MovieLens.")
        if user_id not in catalog.knn.users:
            raise HTTPException(404, "Profil MovieLens introuvable.")

    if mode == "content":
        ranking = catalog.content.rank(movie_id)
    elif mode == "collaborative":
        ranking = catalog.knn.rank(user_id)
    else:
        similar = catalog.content.rank(movie_id, excluded=catalog.knn.seen(user_id))
        collaborative = catalog.knn.rank(user_id).drop(movie_id, errors="ignore")
        ranking = hybrid_rank(similar, collaborative)
    scores = ranking.head(limit)
    return {"mode": mode, "movies": catalog.records(scores.index, scores)}


@app.get("/api/evaluation")
def evaluation(request: Request):
    return request.app.state.catalog.results
