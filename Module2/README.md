# ImmoAnalyse --- Module 2 : Préparation des données pour le Machine Learning

## Présentation

Ce module prolonge le Module 1, dans lequel les données immobilières ont
déjà été traitées et consolidées. L'objectif est de réaliser l'analyse
exploratoire, de préparer les variables et de construire un pipeline de
prétraitement reproductible, afin de fournir des données fiables au
module de modélisation.

## Objectifs

-   Auditer le dataset issu du Module 1.
-   Comprendre les distributions et les relations entre variables.
-   Identifier et traiter les anomalies restantes.
-   Construire des variables pertinentes pour la prédiction des prix immobiliers.
-   Préparer les variables numériques et catégorielles.
-   Séparer les données sans fuite d'information.
-   Construire, valider et sérialiser un pipeline de prétraitement.
-   Documenter les décisions et les résultats.

## Étapes du projet

### 1. Chargement et audit des données

-   Charger le dataset du Module 1.
-   Vérifier dimensions, types, valeurs manquantes, doublons et
    cohérence.
-   Identifier la variable cible (prix immobilier) et les variables
    explicatives.

**Livrable :** dataset audité et prêt pour l'EDA.

### 2. Analyse exploratoire (EDA)

-   Étudier les distributions des variables numériques.
-   Examiner les fréquences des variables catégorielles.
-   Analyser les corrélations et les relations avec la cible.
-   Visualiser les tendances et les observations atypiques.

**Livrable :** notebook EDA et synthèse des principaux constats.

### 3. Traitement des anomalies

-   Détecter les valeurs aberrantes et incohérences métier.
-   Définir une stratégie documentée : conserver, corriger ou exclure.
-   Éviter les suppressions automatiques sans justification.

**Livrable :** données contrôlées et décisions documentées.

### 4. Feature Engineering

-   Créer des variables métier pertinentes.
-   Extraire les informations utiles des variables temporelles ou
    géographiques, si disponibles.
-   Évaluer la pertinence des variables dérivées.
-   Écarter les variables qui provoqueraient une fuite de la cible.

**Livrable :** dataset enrichi et dictionnaire des nouvelles variables.

### 5. Prétraitement des variables

-   Séparer les variables explicatives `X` de la cible `y`.
-   Identifier les variables numériques et catégorielles.
-   Définir les imputations nécessaires.
-   Encoder les variables catégorielles.
-   Mettre à l'échelle les variables numériques lorsque cela est
    pertinent.

**Livrable :** transformations définies pour les données d'entraînement.

### 6. Séparation des données

-   Constituer les ensembles train, validation et test.
-   Choisir une stratégie adaptée à la structure des données.
-   Prévenir toute fuite d'information entre les ensembles.

**Livrable :** partitions indépendantes et reproductibles.

### 7. Construction du pipeline

-   Implémenter les transformations avec `ColumnTransformer`.
-   Combiner prétraitement et transformations dans un pipeline
    `scikit-learn`.
-   Ajuster les transformations uniquement sur les données
    d'entraînement.

**Livrable :** pipeline de prétraitement reproductible.

### 8. Validation qualité

-   Vérifier les dimensions et les types après transformation.
-   Contrôler les valeurs manquantes, infinies et les incohérences.
-   Vérifier la reproductibilité et la compatibilité des
    transformations.

**Livrable :** rapport de validation qualité.

### 9. Export et documentation

-   Exporter les données préparées selon les besoins du projet.
-   Sérialiser le pipeline avec `joblib`.
-   Documenter les choix, les hypothèses et les limites.

**Livrable final :** données et pipeline prêts pour le Module 3
(modélisation).

## Ordre d'exécution recommandé

`Audit → EDA → Anomalies → Feature Engineering → Prétraitement → Split → Pipeline → Validation → Export`

## Technologies

-   Python
-   pandas
-   NumPy
-   Matplotlib / Seaborn
-   scikit-learn
-   joblib
-   Jupyter Notebook

## Structure indicative

``` text
ImmoAnalyse/
├── data/
│   ├── raw/                 # Données d'entrée du Module 1
│   └── processed/           # Données préparées du Module 2
├── notebooks/
│   └── module_02_preparation.ipynb
├── src/
│   └── preprocessing.py     # Pipeline et fonctions de préparation
├── reports/
│   └── figures/             # Visualisations et rapports
├── models/
│   └── preprocessing_pipeline.joblib
├── requirements.txt
└── README.md
```

Cette structure est indicative et peut être adaptée à l'organisation
réelle du dépôt.

## Reproductibilité

-   Fixer les graines aléatoires lorsque nécessaire (`random_state`).
-   Garder les transformations dans le pipeline.
-   Ne jamais ajuster les imputations, encodeurs ou scalers sur les
    données de validation ou de test.
-   Documenter les versions des dépendances et les décisions de
    préparation.

## Résultat attendu

À la fin du Module 2, le projet doit disposer d'un dataset préparé, d'un
pipeline de prétraitement sérialisé, de rapports de contrôle qualité et
d'une documentation permettant de passer au Module 3.
