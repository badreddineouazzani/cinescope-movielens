"""Évalue hors interface le moteur par titre sur le split officiel MovieLens."""
import pandas as pd

from big_data.storage import ROOT, load, read_split
from backend.algorithm.tfidf import ContentModel
from backend.popularity import popularity


def evaluate():
    movies, _ = load()
    train, test = read_split()
    content = ContentModel(movies)
    baseline = popularity(train).index
    history = train.groupby("user_id")["movie_id"].agg(set)
    seeds = (
        train.loc[train["rating"] >= 4]
        .sort_values(["rating", "rated_at", "movie_id"], ascending=[False, False, True])
        .drop_duplicates("user_id").set_index("user_id")["movie_id"]
    )
    results = []
    for user_id, rows in test.groupby("user_id"):
        relevant = set(rows.loc[rows["rating"] >= 4, "movie_id"])
        if user_id not in seeds.index or not relevant:
            continue
        seen = history.loc[user_id]
        rankings = {
            "Top films (référence)": baseline.difference(seen, sort=False),
            "Films similaires": content.rank(seeds.loc[user_id], excluded=seen).index,
        }
        results.append({label: len(set(ids[:10]) & relevant) / 10 for label, ids in rankings.items()})
    metrics = pd.DataFrame(results).mean().rename("Precision@10").rename_axis("classement").reset_index()
    metrics["profils test"] = len(results)
    return metrics


if __name__ == "__main__":
    metrics = evaluate()
    metrics.to_csv(ROOT / "artifacts" / "metriques_classement.csv", index=False)
    print(metrics.to_string(index=False))
