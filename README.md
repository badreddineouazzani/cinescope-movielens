# CinéScope · Movie Recommender

Plateforme académique **Big Data et Machine Learning** pour explorer MovieLens 100K. Le projet reprend le backlog du PowerPoint et ajoute un sprint d’intégration Spark, FastAPI et livraison.

## Lancement local sur macOS

Python 3.12 ou une version compatible avec les paquets épinglés, Java 17+ et Node.js 22.12+ (LTS recommandé). Anaconda et Jupyter peuvent être réutilisés. Dans le dossier du projet :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-bigdata.txt
python -m big_data.prepare ~/Downloads/ml-100k.zip
python -m big_data.evaluate
npm --prefix frontend ci
npm --prefix frontend run build
python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Ouvrir [la plateforme](http://127.0.0.1:8765/) ou [Swagger](http://127.0.0.1:8765/docs). Pour relancer les notebooks, ouvrir les notebooks du dossier `notebooks/` dans Jupyter avec un noyau Python disposant des dépendances du projet et de Matplotlib. Exécuter le pipeline avant de les ouvrir.

## Architecture

`ml-100k.zip → Spark ETL local → Parquet et CSV → TF-IDF (NumPy) → FastAPI → interface web`

Spark lit l’archive fournie avec des schémas explicites, convertit le catalogue en UTF-8, contrôle les notes, supprime les doublons et filtre les clés invalides. Les fichiers Parquet servent à l’application et aux notebooks. Les CSV nettoyés sont disponibles dans `data/`. Le split officiel a 80 000 notes d’apprentissage et 20 000 notes de test. Les données restent locales. [GroupLens et conditions d’utilisation](https://grouplens.org/datasets/movielens/100k/).

L’interface reprend le quadrillage clair et les accents indigo et jaune visibles dans Miro. Photo du cinéma en couverture. [Denise Jans sur Unsplash](https://unsplash.com/photos/a-theater-with-red-seats-and-a-projector-screen-k1bRs5Nvq4c).

## Organisation du dépôt

| Fichier | Rôle |
| --- | --- |
| [frontend/src/main.jsx](frontend/src/main.jsx) | Point d’entrée React et navigation |
| [frontend/src/components/Recommendations.jsx](frontend/src/components/Recommendations.jsx) | Recherche par titre, résultats et contrôles de filtre |
| [frontend/src/api.js](frontend/src/api.js) | Requêtes HTTP du frontend vers FastAPI |
| [backend/api.py](backend/api.py) | Routes FastAPI, validation des paramètres et réponses JSON |
| [backend/recommendation_filters.py](backend/recommendation_filters.py) | Filtrage des suggestions par genre et décennie avant la limite de résultats |
| [backend/algorithm/tfidf.py](backend/algorithm/tfidf.py) | TF-IDF sur les genres et classement par similarité cosinus |
| [big_data/prepare.py](big_data/prepare.py) | Lecture de l’archive MovieLens avec Spark et export Parquet/CSV |
| [big_data/cleaning.py](big_data/cleaning.py) | Suppression des doublons, validation des notes et des identifiants |
| [big_data/storage.py](big_data/storage.py) | Lecture des tables Parquet et du découpage officiel |
| [big_data/evaluate.py](big_data/evaluate.py) | Évaluation du moteur sur MovieLens, export des métriques |
| [notebooks/](notebooks/) | Analyse exploratoire et évaluation |
| [docs/](docs/) | Rapport et backlog des sprints |

Pour développer avec le rechargement React, gardez FastAPI sur le port 8765 et lancez `npm --prefix frontend run dev` dans un deuxième terminal. Vite transmet les requêtes `/api` à FastAPI.

## Moteur de recommandation

Le serveur applique **TF-IDF sur les genres et la similarité cosinus**. Le moteur reçoit le film choisi, exclut ce titre puis renvoie jusqu’à dix films avec un genre en commun. L’utilisateur peut s’en servir sans profil ni historique. L’évaluation reste dans [le rapport](docs/RAPPORT.md) et les notebooks.

## Parcours de démonstration

1. **Découvrir** — afficher les films les mieux notés et modifier le seuil de votes.
2. **Recommandations** — chercher et sélectionner un film, puis afficher les films similaires.
3. **Analyse** — consulter les chiffres du catalogue, la distribution des notes et les films les plus notés.

## Sprints et suivi

| Sprint | User Stories | Charge | SP |
| --- | --- | ---: | ---: |
| 1 · Données et Top 10 | US1 à US6 | 18 h | 10 |
| 2 · Recommandations et évaluation | US7 à US11 | 20 h | 11 |
| 3 · Spark, FastAPI et livraison | US12 à US15 | 14 h | 10 |

Le [backlog d’origine](docs/BACKLOG.csv) contient les 35 tâches des deux premiers sprints. Le [plan de livraison](docs/sprints.json) contient les 15 histoires et leur découpage. Le Sprint 3 couvre la migration vers FastAPI, le pipeline Spark, les tests et la publication. Le backlog d’origine conserve les pistes étudiées, tandis que la version actuelle sert un seul moteur. [Board Miro](https://miro.com/app/board/uXjVEO5AXXU=/).

## Déploiement Vercel

Importer le dépôt privé ou exécuter `vercel deploy` après connexion. Vercel compile React avec Vite, puis déploie le point d’entrée FastAPI `main:app` avec `requirements.txt`. FastAPI sert la version compilée de React. Sur Vercel, le catalogue est chargé depuis l’archive officielle GroupLens à l’initialisation de l’instance. Le pipeline Spark reste une étape locale. Les algorithmes TF-IDF et cosinus utilisent les opérations matricielles de NumPy, ce qui réduit la taille du déploiement. L’archive et les exports détaillés sont exclus du dépôt et des fichiers envoyés au déploiement.

Lancer `python tests/smoke.py URL` contre l’instance. Vérifier la page d’accueil, `/api/health`, `/api/stats`, une recommandation et `/docs`. [Guide FastAPI sur Vercel](https://vercel.com/docs/frameworks/backend/fastapi).
