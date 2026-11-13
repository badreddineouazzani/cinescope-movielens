# Rapport technique · Movie Recommender

**Chaymae Tajry et Said Belyamani**
**Encadrement** Mme Fatima Gueroute

## Objectif

Aider un utilisateur à découvrir des films à partir d’un titre choisi. Le premier sprint fournit le classement de référence et l’analyse des données. Le second ajoute le moteur de recommandation et son évaluation.

## Sprint 1 · Préparation et classement

MovieLens 100K contient 100 000 notes sur 1 682 films, données par 943 utilisateurs. Le pipeline contrôle les identifiants et les notes de 1 à 5, retire les doublons utilisateur-film et convertit les timestamps en dates UTC. Les 19 indicateurs du catalogue servent à construire le vecteur de genres. Le moteur écarte l’indicateur « genre inconnu ». L’application affiche les 10 films ayant la meilleure note moyenne après application d’un seuil de votes, fixé à 20 par défaut.

## Sprint 2 · Recommandations et évaluation

KNN cherche les films les plus proches du titre sélectionné. Chaque genre est représenté par une valeur binaire. La distance de Jaccard vaut 1 moins la proportion de genres communs parmi les genres distincts des deux films. Les distances les plus faibles passent en tête. Le moteur écarte le film choisi et les films sans genre commun. Les filtres s’appliquent avant la sélection des dix voisins.

L’évaluation repose sur `u1.base` et `u1.test`. Pour chacun des 456 profils éligibles, le moteur prend un titre bien noté dans l’apprentissage, puis vérifie combien des dix suggestions figurent parmi les films notés au moins 4/5 dans le test. Le classement Top films utilise le même jeu d’apprentissage et les mêmes profils.

| Classement | Precision@10 |
| --- | ---: |
| Top films (référence) | 11,34 % |
| KNN par genre | 5,31 % |

Le classement Top films retrouve davantage de films bien notés dans ce test. Le moteur par genre répond à un usage différent. Il propose des titres proches d’un film que l’utilisateur vient de choisir. Le catalogue contient 19 indicateurs de genre. Les films sans note de test ne sont pas comptés comme pertinents.

## Sprint 3 · Intégration Big Data et FastAPI

Apache Spark lit et transforme les notes et le catalogue en partitions locales. Il conserve le découpage officiel et produit des tables Parquet. FastAPI charge les vecteurs de genres au démarrage et calcule les voisins à la demande. L’interface affiche les films suggérés et les statistiques du catalogue. Les performances distribuées restent à mesurer sur un jeu de taille supérieure à MovieLens 100K.

## Reproduction

Exécuter `python -m big_data.prepare ~/Downloads/ml-100k.zip` puis `python -m big_data.evaluate`. Le script enregistre la comparaison dans `artifacts/metriques_classement.csv`. Les notebooks présentent la préparation et les résultats.

Source des données et du découpage officiel. [GroupLens, MovieLens 100K](https://grouplens.org/datasets/movielens/100k/). [Harper et Konstan, 2015](https://doi.org/10.1145/2827872).
