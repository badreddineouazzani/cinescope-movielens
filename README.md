# CinéScope · Movie Recommender

Plateforme académique **Big Data et Machine Learning** pour explorer MovieLens 100K. Le projet reprend le backlog du PowerPoint et ajoute un sprint d’intégration Spark, FastAPI et livraison.

## Lancement local sur macOS

Python 3.12 ou une version compatible avec les paquets épinglés, et Java 17+. Anaconda et Jupyter peuvent être réutilisés. Dans le dossier du projet :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-bigdata.txt
python pipeline.py ~/Downloads/ml-100k.zip
python evaluate.py
python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Ouvrir [la plateforme](http://127.0.0.1:8765/) ou [Swagger](http://127.0.0.1:8765/docs). Pour relancer les notebooks, ouvrir Jupyter dans le dossier du projet avec un noyau Python disposant des dépendances du projet et de Matplotlib. Exécuter le pipeline avant de les ouvrir.

## Architecture

`ml-100k.zip → Spark ETL local → Parquet et CSV → TF-IDF / k-NN (NumPy) → FastAPI → interface web`

Spark lit l’archive fournie avec des schémas explicites, convertit le catalogue en UTF-8, contrôle les notes, supprime les doublons et filtre les clés invalides. Les fichiers Parquet servent à l’application et aux notebooks. Les CSV nettoyés sont disponibles dans `data/`. Le split officiel a 80 000 notes d’apprentissage et 20 000 notes de test. Les données restent locales. [GroupLens et conditions d’utilisation](https://grouplens.org/datasets/movielens/100k/).

L’interface reprend le quadrillage clair et les accents indigo et jaune visibles dans Miro. Photo du cinéma en couverture. [Denise Jans sur Unsplash](https://unsplash.com/photos/a-theater-with-red-seats-and-a-projector-screen-k1bRs5Nvq4c).

## Algorithmes

| Mode | Méthode |
| --- | --- |
| Top films | Moyenne des notes et seuil de votes. Seuil initial de 20 votes. |
| Films similaires | TF-IDF sur les 19 indicateurs de genres et similarité cosinus. |
| Collaboratif | k-NN utilisateur-utilisateur. Les 30 voisins les plus proches contribuent par moyenne centrée pondérée. |
| Hybride | Fusion des rangs réciproques du contenu et du collaboratif. Les films déjà notés et le film de départ sont exclus. |

La note moyenne du film, ou la moyenne globale, sert de repli lorsqu’aucun voisin ne peut prédire une note. Les résultats sur le split officiel figurent dans [le rapport](RAPPORT.md) et dans l’onglet Évaluation.

## Parcours de démonstration

1. **Découvrir** — montrer le Top 10 et modifier le seuil de votes.
2. **Recommandations** — choisir Toy Story, puis essayer le profil 1 en mode collaboratif et hybride.
3. **Analyse** — montrer les 100 000 notes, 1 682 films et 943 profils, puis la distribution des notes.
4. **Évaluation** — comparer RMSE/MAE et Precision@10. Ouvrir `/docs` pour tester l’API.

## Sprints et suivi

| Sprint | User Stories | Charge | SP |
| --- | --- | ---: | ---: |
| 1 · Données et Top 10 | US1 à US6 | 18 h | 10 |
| 2 · Recommandations et évaluation | US7 à US11 | 20 h | 11 |
| 3 · Spark, FastAPI et livraison | US12 à US15 | 14 h | 10 |

Le [backlog d’origine](BACKLOG.csv) contient les 35 tâches des deux premiers sprints. Le [plan de livraison](sprints.json) contient les 15 histoires et leur découpage. Le Sprint 3 couvre la migration vers FastAPI, le pipeline Spark, les tests et la publication.

## Déploiement Vercel

Importer le dépôt privé ou exécuter `vercel deploy` après connexion. Vercel détecte le point d’entrée FastAPI `main:app` et utilise `requirements.txt`. Sur Vercel, le catalogue est chargé depuis l’archive officielle GroupLens à l’initialisation de l’instance. Le pipeline Spark reste une étape locale. Les algorithmes TF-IDF et cosinus utilisent les opérations matricielles de NumPy, ce qui réduit la taille du déploiement. L’archive et les exports détaillés sont exclus du dépôt et des fichiers envoyés au déploiement.

Lancer `python tests/smoke.py URL` contre l’instance. Vérifier la page d’accueil, `/api/health`, `/api/stats`, une recommandation et `/docs`. [Guide FastAPI sur Vercel](https://vercel.com/docs/frameworks/backend/fastapi).
