# 🏠 IMMO_ANALYSE — Analyse et qualité des données immobilières

## 📌 Présentation du projet

**IMMO_ANALYSE** est un projet de collecte, de nettoyage, de validation et d’analyse de données immobilières provenant de plusieurs sources.

L’objectif principal est de transformer des données brutes, souvent hétérogènes et incomplètes, en données fiables, structurées et exploitables pour faciliter l’analyse du marché immobilier et la prise de décision.

Ce projet met en pratique plusieurs compétences en **data engineering, data cleaning, contrôle qualité, analyse exploratoire et visualisation de données**.

## 🎯 Objectifs

- Collecter et centraliser des données immobilières provenant de différentes sources.
- Harmoniser les formats et les structures des fichiers CSV, Excel et JSON.
- Détecter et traiter les valeurs manquantes, incohérences et doublons.
- Appliquer des règles de validation adaptées aux données immobilières.
- Identifier les données invalides et les isoler dans un fichier de quarantaine.
- Mesurer la qualité des données avant et après le nettoyage.
- Produire des indicateurs utiles à l’analyse du marché immobilier.
- Visualiser les résultats à travers un tableau de bord interactif avec Dash.
- Assurer la traçabilité des transformations effectuées sur les données.

## 🗂️ Sources de données

Le projet est conçu pour exploiter plusieurs formats de données :

| Format | Utilisation |
|---|---|
| CSV | Importation de données immobilières tabulaires |
| Excel (XLSX) | Intégration de fichiers provenant de différentes sources |
| JSON | Traitement de données structurées ou imbriquées |
| Fichiers de référence | Harmonisation et validation des catégories et des valeurs |

Les données peuvent contenir des informations telles que le prix du bien, la superficie, le nombre de pièces, la localisation, le type de bien, le type de transaction et la source de publication.

## ⚙️ Fonctionnement du pipeline

Le traitement suit plusieurs étapes :

1. **Ingestion** : récupération des données issues des différentes sources.
2. **Normalisation** : harmonisation des noms de colonnes, des formats et des types de données.
3. **Nettoyage** : traitement des valeurs manquantes et des incohérences.
4. **Validation** : application des règles métier pour vérifier la cohérence des informations.
5. **Détection des doublons** : identification des enregistrements identiques ou potentiellement similaires.
6. **Quarantaine** : séparation des données qui ne respectent pas les règles de qualité.
7. **Audit** : enregistrement des contrôles et des résultats du traitement.
8. **Analyse** : calcul des indicateurs et exploration des données nettoyées.
9. **Visualisation** : présentation des résultats dans un tableau de bord interactif.

### 🔄 Schéma du traitement

```text
Sources immobilières
        │
        ▼
Ingestion des données
        │
        ▼
Normalisation des formats
        │
        ▼
Nettoyage et validation
        │
        ├──────────────► Données en quarantaine
        │
        ▼
Détection des doublons
        │
        ▼
Données nettoyées
        │
        ├──────────────► Audit et indicateurs qualité
        │
        ▼
Analyse exploratoire
        │
        ▼
Tableau de bord Dash
```

## 🧹 Règles de qualité des données

Plusieurs contrôles peuvent être appliqués au cours du traitement :

- Vérification de la présence des champs essentiels.
- Contrôle des valeurs numériques, notamment le prix et la superficie.
- Détection des prix ou superficies non valides.
- Harmonisation des catégories de biens et des types de transaction.
- Identification des doublons exacts et probables.
- Détection des incohérences entre les champs.
- Conservation des informations nécessaires à la traçabilité.
- Mise en quarantaine des enregistrements qui nécessitent une vérification.

Les données écartées ne sont pas simplement supprimées : leur séparation permet de conserver une trace des anomalies et de faciliter leur analyse.

## 📊 Tableau de bord interactif

Le projet comprend un tableau de bord développé avec **Dash et Plotly** afin de faciliter l’exploration des résultats.

### Principales vues

- **Vue générale** : présentation des indicateurs clés du traitement.
- **Qualité avant/après** : comparaison de la complétude des données avant et après nettoyage.
- **Analyse immobilière** : exploration des prix, superficies, catégories de biens et localisations.
- **Sources et traçabilité** : suivi des volumes de données provenant des différentes sources.
- **Quarantaine** : analyse des enregistrements rejetés et des motifs associés.

### Indicateurs suivis

- Nombre de lignes avant nettoyage.
- Nombre de lignes conservées après nettoyage.
- Nombre et proportion de données mises en quarantaine.
- Nombre de valeurs manquantes sur les champs importants.
- Nombre de doublons détectés.
- Prix médian des biens.
- Superficie médiane.
- Prix médian au mètre carré.
- Répartition des biens par catégorie, région et source.

Ces indicateurs permettent d’évaluer la qualité des données et de mieux comprendre les tendances observées dans le jeu de données traité.

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python | Développement du pipeline de traitement |
| Pandas | Manipulation et nettoyage des données |
| NumPy | Calculs et opérations numériques |
| OpenPyXL | Lecture et traitement des fichiers Excel |
| JSON | Traitement des données structurées |
| Plotly | Création de graphiques interactifs |
| Dash | Développement du tableau de bord |
| Pytest | Tests et vérification du fonctionnement |
| Git et GitHub | Gestion du code source et versionnement |

## 📁 Structure du projet

```text
IMMO_ANALYSE/
│
├── data/
│   ├── raw/                 # Données brutes
│   ├── staging/             # Données intermédiaires
│   ├── processed/           # Données nettoyées
│   └── reference/           # Fichiers de référence
│
├── dashboard/
│   ├── app.py               # Application Dash
│   └── assets/
│       └── style.css        # Styles du tableau de bord
│
├── notebooks/               # Analyses exploratoires
├── tests/                   # Tests automatisés
├── sortie/                  # Audits et résultats exportés
├── main.py                  # Point d'entrée du pipeline
├── requirements.txt         # Dépendances Python
└── README.md                # Documentation du projet
```

*L’organisation exacte peut varier selon les modules et fichiers présents dans le dépôt.*

## 🚀 Installation et démarrage

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd IMMO_ANALYSE
```

Remplacer `<URL_DU_DEPOT>` par l’adresse réelle du dépôt GitHub.

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Activer l’environnement :

**Sous Windows :**

```bash
.venv\Scripts\activate
```

**Sous Linux ou macOS :**

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Exécuter le pipeline de traitement

```bash
python main.py
```

Cette commande lance le traitement principal, sous réserve que le point d’entrée et les fichiers de configuration soient correctement renseignés.

### 5. Lancer le tableau de bord

```bash
python dashboard/app.py
```

Une fois l’application démarrée, ouvrir l’adresse suivante dans un navigateur :

```text
http://127.0.0.1:8050
```

**Important :** le tableau de bord doit disposer des fichiers de données attendus par l’application. Les chemins et les noms des fichiers doivent correspondre à la configuration du projet.

## 🧪 Tests

Les tests automatisés peuvent être exécutés avec :

```bash
python -m pytest -v
```

Ils permettent de vérifier les différentes fonctionnalités couvertes par la suite de tests, notamment les transformations et les règles de validation.

## 📈 Résultats attendus

Le projet vise à produire :

- Des données immobilières normalisées et structurées.
- Un jeu de données nettoyé pour les analyses.
- Un fichier de quarantaine contenant les enregistrements à examiner.
- Des rapports d’audit sur les opérations de traitement.
- Des indicateurs de qualité avant et après nettoyage.
- Des visualisations pour explorer les caractéristiques du marché immobilier.
- Un tableau de bord facilitant l’interprétation des résultats.

La fiabilité des analyses dépend de la qualité des données d’entrée, des règles de validation appliquées et de la couverture des tests.

## 🔐 Bonnes pratiques

- Conserver les données brutes sans les modifier directement.
- Documenter les transformations appliquées aux données.
- Séparer les données nettoyées des enregistrements en quarantaine.
- Éviter de publier des données personnelles ou confidentielles sur GitHub.
- Exclure les environnements virtuels, fichiers temporaires et données sensibles du dépôt.
- Utiliser Git pour suivre les évolutions du code.
- Vérifier les résultats du pipeline avant toute analyse ou interprétation.

## 🔮 Perspectives d'amélioration

Plusieurs évolutions peuvent enrichir le projet :

- Ajouter de nouvelles sources de données immobilières.
- Améliorer les règles de détection des doublons probables.
- Enrichir les rapports de qualité et de traçabilité.
- Ajouter des filtres et des visualisations au tableau de bord.
- Automatiser l’exécution du pipeline.
- Mettre en place une intégration continue pour exécuter les tests à chaque modification.
- Développer des analyses plus approfondies sur les prix et les tendances régionales.

## 👤 À propos

**IMMO_ANALYSE** est un projet de data engineering et d’analyse de données immobilières, conçu pour transformer des données hétérogènes en informations structurées, contrôlées et exploitables.

Il met l’accent sur la qualité des données, la traçabilité des traitements et la visualisation des résultats.

## 📄 Licence

La licence reste à définir selon les conditions de diffusion du projet. Avant toute publication, un fichier `LICENSE` peut être ajouté au dépôt pour préciser les droits d’utilisation, de modification et de redistribution.