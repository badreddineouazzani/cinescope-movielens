# CinéScope · Movie Recommender

Plateforme académique **Big Data et Machine Learning** pour explorer MovieLens 100K. Le projet reprend la préparation des données avec Pandas prévue dans la présentation initiale. Un troisième sprint couvre l’intégration de FastAPI et de React ainsi que la livraison.

## Lancement local sur macOS

Python 3.12 ou une version compatible avec les paquets épinglés et Node.js 22.12+ (LTS recommandé). Anaconda et Jupyter peuvent être réutilisés. Dans le dossier du projet :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m data_science.prepare ~/Downloads/ml-100k.zip
npm --prefix frontend ci
npm --prefix frontend run build
python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Ouvrir [la plateforme](http://127.0.0.1:8765/) ou [Swagger](http://127.0.0.1:8765/docs). Pour relancer les notebooks dans Jupyter, préparez d’abord les CSV et utilisez un noyau Python disposant des dépendances du projet et de Matplotlib.

## Architecture

`ml-100k.zip → Pandas → CSV → KNN (NumPy) → FastAPI → React`

Pandas lit l’archive MovieLens, contrôle les notes et les identifiants, retire les doublons et exporte quatre fichiers UTF-8 dans `data/`. `movies.csv` et `ratings.csv` alimentent l’application locale et les notebooks. `train.csv` et `test.csv` conservent le découpage officiel de 80 000 notes d’apprentissage et 20 000 notes de test. MovieLens 100K tient en mémoire sur un poste de travail. [GroupLens et conditions d’utilisation](https://grouplens.org/datasets/movielens/100k/).

L’interface reprend le quadrillage clair et les accents indigo et jaune visibles dans Miro. Photo du cinéma en couverture. [Denise Jans sur Unsplash](https://unsplash.com/photos/a-theater-with-red-seats-and-a-projector-screen-k1bRs5Nvq4c).

## Organisation du dépôt

`frontend/` contient l’interface React. `api_service/` expose le catalogue et les recommandations via FastAPI. `data_science/` regroupe la préparation Pandas, le moteur KNN et son évaluation. Les données générées localement sont dans `data/`.

| Fichier | Rôle |
| --- | --- |
| [frontend/src/main.jsx](frontend/src/main.jsx) | Point d’entrée React et navigation |
| [frontend/src/components/Recommendations.jsx](frontend/src/components/Recommendations.jsx) | Recherche par titre, résultats et contrôles de filtre |
| [frontend/src/api.js](frontend/src/api.js) | Requêtes HTTP du frontend vers FastAPI |
| [api_service/api.py](api_service/api.py) | Routes FastAPI, validation des paramètres et réponses JSON |
| [api_service/recommendation_filters.py](api_service/recommendation_filters.py) | Filtrage des suggestions par genre et décennie avant la limite de résultats |
| [data_science/knn.py](data_science/knn.py) | K plus proches voisins selon le genre, l’année, la note et le nombre de votes |
| [data_science/archive.py](data_science/archive.py) | Lecture de l’archive MovieLens avec Pandas en local et sur Vercel |
| [data_science/prepare.py](data_science/prepare.py) | Export local des quatre tables nettoyées en CSV |
| [data_science/cleaning.py](data_science/cleaning.py) | Suppression des doublons, validation des notes et des identifiants |
| [data_science/storage.py](data_science/storage.py) | Lecture des tables CSV et du découpage officiel |
| [data_science/evaluate.py](data_science/evaluate.py) | Calcul de Precision@10, réutilisable depuis Python et Jupyter |
| [notebooks/Sprint_1_Analyse.ipynb](notebooks/Sprint_1_Analyse.ipynb) | Exploration du catalogue et des notes |
| [notebooks/Sprint_2_Evaluation.ipynb](notebooks/Sprint_2_Evaluation.ipynb) | Présentation du protocole et des résultats du Sprint 2 |
| [docs/](docs/) | Rapport et backlog des sprints |

Pour développer avec le rechargement React, gardez FastAPI sur le port 8765 et lancez `npm --prefix frontend run dev` dans un deuxième terminal. Vite transmet les requêtes `/api` à FastAPI.

## Moteur de recommandation

Le serveur utilise **KNN (K plus proches voisins)**. Il compare les films qui partagent au moins un genre avec le titre choisi. La distance combine les genres (60 %), l’année de sortie (15 %), la note moyenne (15 %) et le nombre de votes (10 %). Le nombre de votes passe sur une échelle logarithmique pour atténuer les écarts entre les films. Le moteur renvoie jusqu’à dix voisins après application des filtres. L’évaluation figure dans [le rapport](docs/RAPPORT.md).

## Évaluation du Sprint 2

Le notebook appelle la fonction `evaluate()` du script Python et affiche ses résultats. Le calcul utilise le split officiel MovieLens et compare la Precision@10 du KNN au classement Top films.

Pour relancer le même calcul dans le terminal et actualiser `artifacts/metriques_classement.csv`, exécutez `python -m data_science.evaluate` après la préparation des CSV.

## Parcours de démonstration

1. **Découvrir** — afficher les films les mieux notés et modifier le seuil de votes.
2. **Recommandations** — chercher et sélectionner un film, puis afficher les films similaires.
3. **Analyse** — consulter les chiffres du catalogue, la distribution des notes et les films les plus notés.

## Sprints et suivi

| Sprint | User Stories | Charge | SP |
| --- | --- | ---: | ---: |
| 1 · Données et Top 10 | US1 à US6 | 18 h | 10 |
| 2 · Recommandations et évaluation | US7 à US11 | 20 h | 11 |
| 3 · Intégration FastAPI, React et livraison | US12 à US15 | 14 h | 10 |

Le [backlog d’origine](docs/BACKLOG.csv) contient les 35 tâches des deux premiers sprints. Le [plan de livraison](docs/sprints.json) contient les 15 histoires et leur découpage. Le Sprint 3 couvre la validation du pipeline Pandas, l’intégration FastAPI et React, les tests et la publication. Le Product Backlog Jira reprend les intitulés des slides pour US1 à US11. La description de chaque story indique où en est le livrable dans la version actuelle. [Product Backlog Jira](https://um5-team-bdia2627.atlassian.net/issues/?jql=project%20%3D%20CINE%20AND%20issuetype%20%3D%20Story%20ORDER%20BY%20Rank%20ASC) · [Tableau de suivi Jira](https://um5-team-bdia2627.atlassian.net/jira/software/projects/CINE/boards/2) · [Board Miro](https://miro.com/app/board/uXjVEO5AXXU=/).

## Déploiement Vercel

Importer le dépôt privé ou exécuter `vercel deploy` après connexion. Vercel compile React avec Vite, puis déploie le point d’entrée FastAPI `main:app` avec `requirements.txt`. FastAPI sert la version compilée de React. Sur Vercel, le catalogue est chargé depuis l’archive officielle GroupLens à l’initialisation de l’instance. L’instance utilise le même nettoyage Pandas que la préparation locale. KNN calcule les distances entre films avec NumPy. L’archive et les exports détaillés sont exclus du dépôt et des fichiers envoyés au déploiement.

Lancer `python tests/smoke.py URL` contre l’instance. Vérifier la page d’accueil, `/api/health`, `/api/stats`, une recommandation et `/docs`. [Guide FastAPI sur Vercel](https://vercel.com/docs/frameworks/api_service/fastapi).
