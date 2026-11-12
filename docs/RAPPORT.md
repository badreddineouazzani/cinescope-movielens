# Rapport technique · Movie Recommender

**Chaymae Tajry et Said Belyamani**
**Encadrement** Mme Fatima Gueroute

## Objectif

Aider un utilisateur à découvrir des films à partir d’un titre choisi. Le premier sprint fournit le classement de référence et l’analyse des données. Le second ajoute le moteur de recommandation et son évaluation.

## Sprint 1 · Préparation et classement

MovieLens 100K contient 100 000 notes sur 1 682 films, données par 943 utilisateurs. Le pipeline contrôle les identifiants et les notes de 1 à 5, retire les doublons utilisateur-film et convertit les timestamps en dates UTC. Les 19 indicateurs de genre du catalogue servent à construire le texte des genres. L’application affiche les 10 films ayant la meilleure note moyenne après application d’un seuil de votes, fixé à 20 par défaut.

## Sprint 2 · Recommandations et évaluation

Le moteur représente les genres de chaque film avec TF-IDF. Il trie le catalogue selon la similarité cosinus avec le titre sélectionné et exclut ce titre. Un film rare peut avoir moins de dix résultats avec un genre en commun.

L’évaluation repose sur `u1.base` et `u1.test`. Pour chacun des 456 profils éligibles, le moteur prend un titre bien noté dans l’apprentissage, puis vérifie combien des dix suggestions figurent parmi les films notés au moins 4/5 dans le test. Le classement Top films utilise le même jeu d’apprentissage et les mêmes profils.

| Classement | Precision@10 |
| --- | ---: |
| Top films (référence) | 11,34 % |
| Films similaires par genre | 5,11 % |

Le classement Top films retrouve davantage de films bien notés dans ce test. Le moteur par genre répond à un usage différent. Il propose des titres proches d’un film que l’utilisateur vient de choisir. Le catalogue contient 19 indicateurs de genre. Les films sans note de test ne sont pas comptés comme pertinents.

## Sprint 3 · Intégration Big Data et FastAPI

Apache Spark lit et transforme les notes et le catalogue en partitions locales. Il conserve le découpage officiel et produit des tables Parquet. FastAPI charge le catalogue et calcule les similarités au démarrage. L’interface affiche les films suggérés et les statistiques du catalogue. Les performances distribuées restent à mesurer sur un jeu de taille supérieure à MovieLens 100K.

## Reproduction

Exécuter `python -m pipelines.prepare ~/Downloads/ml-100k.zip` puis `python -m pipelines.evaluate`. Le script enregistre la comparaison dans `artifacts/metriques_classement.csv`. Les notebooks présentent la préparation et les résultats.

Source des données et du découpage officiel. [GroupLens, MovieLens 100K](https://grouplens.org/datasets/movielens/100k/). [Harper et Konstan, 2015](https://doi.org/10.1145/2827872).
