"""Évaluation reproductible sur le premier découpage officiel MovieLens 100K."""
import numpy as np
import pandas as pd

from cinescope.data import ROOT, load, read_split
from cinescope.recommender import ContentModel, UserKNN, hybrid_rank, popularity


def evaluate():
    movies, _ = load()
    train, test = read_split()
    content = ContentModel(movies)
    knn = UserKNN(train, movies["movie_id"])
    baseline_rank = popularity(train).index
    seeds = (
        train.loc[train["rating"] >= 4]
        .sort_values(["rating", "rated_at", "movie_id"], ascending=[False, False, True])
        .drop_duplicates("user_id").set_index("user_id")["movie_id"]
    )
    records = []
    predicted = []
    for user_id, rows in test.groupby("user_id", sort=False):
        predicted.append(pd.DataFrame({
            "rating": rows["rating"].to_numpy(),
            "mean": knn.reference.loc[rows["movie_id"]].to_numpy(),
            "knn": knn.predict(user_id).loc[rows["movie_id"]].to_numpy(),
        }))
        relevant = set(rows.loc[rows["rating"] >= 4, "movie_id"])
        if user_id not in seeds.index or not relevant:
            continue
        seen = knn.seen(user_id)
        seed = seeds.loc[user_id]
        similar = content.rank(seed, excluded=seen)
        collaborative = knn.rank(user_id)
        rankings = {
            "Top films": baseline_rank.difference(seen, sort=False),
            "TF-IDF": similar.index,
            "k-NN": collaborative.index,
            "Hybride": hybrid_rank(similar, collaborative).index,
        }
        records.append({label: len(set(ids[:10]) & relevant) / 10 for label, ids in rankings.items()})
    predictions = pd.concat(predicted, ignore_index=True)
    errors = predictions[["mean", "knn"]].sub(predictions["rating"], axis=0)
    rating_metrics = pd.DataFrame({
        "modèle": ["Moyenne par film", "k-NN"],
        "RMSE": np.sqrt((errors ** 2).mean()).to_numpy(),
        "MAE": errors.abs().mean().to_numpy(),
        "notes test": len(predictions),
    })
    ranking = pd.DataFrame(records)
    ranking_metrics = ranking.mean().rename("Precision@10").rename_axis("modèle").reset_index()
    ranking_metrics["utilisateurs test"] = len(ranking)
    return rating_metrics, ranking_metrics


if __name__ == "__main__":
    rating, ranking = evaluate()
    rating.to_csv(ROOT / "artifacts" / "metriques_notes.csv", index=False)
    ranking.to_csv(ROOT / "artifacts" / "metriques_classement.csv", index=False)
    print(rating.to_string(index=False))
    print(ranking.to_string(index=False))
