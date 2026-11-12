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
    for mode, params in [
        ("content", {"movie_id": 1}),
        ("collaborative", {"user_id": 1}),
        ("hybrid", {"movie_id": 1, "user_id": 1}),
    ]:
        rows = get("/api/recommendations", mode=mode, **params)["movies"]
        assert len(rows) == len({row["id"] for row in rows}) == 10, mode
        assert 1 not in {row["id"] for row in rows} or mode == "collaborative"
        scores = [row["score"] for row in rows]
        assert scores == sorted(scores, reverse=True)
        if mode == "collaborative":
            assert all(1 <= score <= 5 for score in scores)

    for params, expected in [({"mode": "hybrid", "movie_id": 1}, 422),
                             ({"mode": "content", "movie_id": 5000}, 404)]:
        try:
            get("/api/recommendations", **params)
        except HTTPError as error:
            assert error.code == expected
        else:
            raise AssertionError(f"HTTP {expected} attendu")

    results = get("/api/evaluation")
    assert len(results["ratings"]) == 2 and len(results["ranking"]) == 4
    assert "/api/recommendations" in get("/openapi.json")["paths"]
    print("CinéScope : santé, données, Top 10, recherche, 3 modes, métriques et OpenAPI vérifiés.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", default="http://127.0.0.1:8765")
    smoke(parser.parse_args().base)
