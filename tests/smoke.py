"""Vérifie une instance CinéScope en cours d’exécution."""
import argparse
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def smoke(base):
    def get(path, **params):
        url = base.rstrip("/") + path
        if params:
            url += "?" + urlencode(params)
        with urlopen(url, timeout=35) as response:
            return json.load(response)

    assert get("/api/health") == {"status": "ok"}
    stats = get("/api/stats")
    assert (stats["movies"], stats["ratings"], stats["users"]) == (1682, 100000, 943)
    assert sum(row["count"] for row in stats["distribution"]) == stats["ratings"]
    popular = get("/api/popular", min_votes=100)
    assert len(popular) == 10 and min(row["votes"] for row in popular) >= 100
    toy_story = get("/api/movies", q="Toy Story")
    assert any(row["id"] == 1 for row in toy_story)
    rows = get("/api/recommendations", movie_id=1)["movies"]
    assert len(rows) == len({row["id"] for row in rows}) == 10
    assert all(row["id"] != 1 and "score" not in row for row in rows)
    toy_genres = set(next(row["genres"] for row in toy_story if row["id"] == 1))
    assert all(toy_genres.intersection(row["genres"]) for row in rows)
    filters = get("/api/recommendation-filters")
    assert "Comedy" in filters["genres"] and 1980 in filters["decades"]
    filtered = get("/api/recommendations", movie_id=1, genre="Comedy", decade=1980)["movies"]
    assert len(filtered) == 10
    assert all("Comedy" in row["genres"] and any(f"({year})" in row["title"]
               for year in range(1980, 1990)) for row in filtered)
    assert {row["id"] for row in filtered} - {row["id"] for row in rows}
    assert get("/api/recommendations", movie_id=1, decade=1800)["movies"] == []
    for params, expected in [
        ({}, 422), ({"movie_id": 5000}, 404), ({"movie_id": 1, "decade": 1985}, 422),
        ({"movie_id": 1, "genre": "Inconnu"}, 422),
    ]:
        try:
            get("/api/recommendations", **params)
        except HTTPError as error:
            assert error.code == expected
        else:
            raise AssertionError(f"HTTP {expected} attendu")

    routes = get("/openapi.json")["paths"]
    recommendation = routes["/api/recommendations"]["get"]
    assert {parameter["name"] for parameter in recommendation["parameters"]} == {"movie_id", "limit", "genre", "decade"}
    assert "/api/evaluation" not in routes
    print("CinéScope : catalogue, recherche, recommandations par titre et OpenAPI vérifiés.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", default="http://127.0.0.1:8765")
    smoke(parser.parse_args().base)
