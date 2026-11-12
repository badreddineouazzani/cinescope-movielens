# Rapport technique · Movie Recommender

**Chaymae Tajry et Said Belyamani**
**Encadrement** Mme Fatima Gueroute

## Objectif

Aider un utilisateur à découvrir des films à partir d’un titre choisi ou d’un historique de notes. Le premier sprint fournit le classement de référence et l’analyse des données. Le second ajoute les modèles et leur évaluation.

## Sprint 1 · Préparation et classement

MovieLens 100K contient 100 000 notes sur 1 682 films, données par 943 utilisateurs. Le pipeline contrôle les identifiants et les notes de 1 à 5, retire les doublons utilisateur-film et convertit les timestamps en dates UTC. Les 19 indicateurs de genre du catalogue servent à construire le texte des genres. L’application affiche les 10 films ayant la meilleure note moyenne après application d’un seuil de votes, fixé à 20 par défaut.

## Sprint 2 · Modèles et protocole

- **TF-IDF par genre** représente chaque film par les genres actifs et compare les vecteurs par similarité cosinus. Le titre de départ est exclu. Un titre rare peut avoir moins de 10 films avec un genre en commun.
- **k-NN collaboratif** utilise les 30 utilisateurs les plus proches par cosinus sur notes centrées. Les écarts à la moyenne sont pondérés par similarité. Pour un film sans vote des voisins, le modèle utilise la moyenne du film ou la moyenne globale.
- **Hybride** fusionne les classements par somme des rangs réciproques, avec un décalage de 60. Les films déjà notés et le film de départ sont exclus.
- **Évaluation** sur le découpage officiel `u1.base` et `u1.test`. Les modèles et références utilisent 80 000 notes d’apprentissage. La prédiction des notes est évaluée sur 20 000 notes de test. Pour le classement, chaque méthode est évaluée sur les mêmes profils, qui ont un film d’amorce noté au moins 4 dans l’apprentissage et au moins un film pertinent dans le test. Une note de test de 4 ou 5 indique la pertinence.

## Résultats

| Prédiction des notes | RMSE | MAE |
| --- | ---: | ---: |
| Moyenne par film | 1,033 | 0,828 |
| k-NN | 1,015 | 0,787 |

| Classement sur 456 profils | Precision@10 |
| --- | ---: |
| Top films | 11,34 % |
| TF-IDF | 5,11 % |
| k-NN | 3,27 % |
| Hybride | 6,56 % |

Sur ce découpage, le k-NN améliore la prédiction des notes par rapport à la moyenne par film. Le Top films obtient la meilleure Precision@10. La fusion dépasse les deux méthodes individuelles de recommandation sur cette mesure. Les films sans note de test ne sont pas comptés comme pertinents. Les résultats décrivent un seul découpage et les genres constituent la seule information utilisée par TF-IDF.

## Sprint 3 · Intégration Big Data et FastAPI

Apache Spark lit et transforme les notes et le catalogue en partitions locales. Il conserve le découpage officiel et produit des tables Parquet. FastAPI charge les modèles au démarrage puis sert le catalogue, les scores et les agrégats. Les performances distribuées restent à mesurer sur un jeu de taille supérieure à MovieLens 100K.

## Reproduction

Exécuter `python pipeline.py ~/Downloads/ml-100k.zip` puis `python evaluate.py`. Les fichiers `metriques_notes.csv` et `metriques_classement.csv` sont lus par FastAPI et affichés dans l’onglet Évaluation. Les notebooks présentent la préparation et les résultats.

Source des données et du découpage officiel. [GroupLens, MovieLens 100K](https://grouplens.org/datasets/movielens/100k/). [Harper et Konstan, 2015](https://doi.org/10.1145/2827872).
