"""
Analyse exploratoire et génération des visualisations.

Toutes les fonctions enregistrent des images PNG dans ``output_dir``.
"""

from pathlib import Path

import matplotlib

# Backend sans écran : permet de générer les figures sur un serveur
# ou en ligne de commande, sans ouvrir de fenêtre.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402


def plot_numeric_distributions(
    df: pd.DataFrame,
    output_dir: Path
) -> None:
    """
    Génère les histogrammes des variables numériques.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset analysé.
    output_dir : Path
        Dossier de sauvegarde des graphiques.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    if not numeric_columns:
        return

    df[numeric_columns].hist(
        figsize=(16, 12),
        bins=30,
        edgecolor="black"
    )

    plt.suptitle("Distributions des variables numériques")
    plt.tight_layout()
    plt.savefig(output_dir / "numeric_distributions.png", dpi=150)
    plt.close("all")


def plot_categorical_frequencies(
    df: pd.DataFrame,
    output_dir: Path,
    max_modalities: int = 15
) -> None:
    """
    Génère un diagramme en barres des fréquences de chaque variable
    catégorielle (étape 2 du plan : « fréquences des variables
    catégorielles », absente du projet d'origine).

    Parameters
    ----------
    max_modalities : int
        Nombre maximal de modalités affichées par variable.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Colonnes texte de faible cardinalité (on ignore id_source, description...)
    categorical_columns = [
        column
        for column in df.select_dtypes(exclude=["number", "bool"]).columns
        if 1 < df[column].nunique() <= 60
    ]

    for column in categorical_columns:
        # dropna=False : on veut voir la part de valeurs manquantes
        counts = (
            df[column]
            .fillna("(manquant)")
            .value_counts()
            .head(max_modalities)
        )

        plt.figure(figsize=(9, 5))
        sns.barplot(x=counts.values, y=counts.index, color="steelblue")
        plt.title(f"Fréquences : {column}")
        plt.xlabel("Nombre d'annonces")
        plt.tight_layout()
        plt.savefig(output_dir / f"freq_{column}.png", dpi=120)
        plt.close("all")


def plot_correlation_matrix(
    df: pd.DataFrame,
    output_dir: Path
) -> None:
    """
    Affiche et sauvegarde la matrice de corrélation numérique.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    numeric_df = df.select_dtypes(include=np.number)

    # Il faut au moins deux variables pour calculer une corrélation
    if numeric_df.shape[1] < 2:
        return

    correlation = numeric_df.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlation,
        cmap="coolwarm",
        center=0,
        annot=True,      # valeurs affichées : plus lisible avec peu de colonnes
        fmt=".2f"
    )
    plt.title("Matrice de corrélation")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_matrix.png", dpi=150)
    plt.close("all")


def plot_target_relationships(
    df: pd.DataFrame,
    target_column: str,
    output_dir: Path
) -> None:
    """
    Génère des graphiques de relation entre les features numériques
    et la variable cible.

    L'axe de la cible est en échelle logarithmique : les prix vont de
    quelques dizaines de milliers (locations) à plusieurs centaines de
    millions de FCFA (ventes), un axe linéaire écraserait tout.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    # Coloration par transaction si disponible (vente / location)
    hue = "transaction" if "transaction" in df.columns else None

    for column in numeric_columns:
        if column == target_column:
            continue

        plt.figure(figsize=(8, 5))
        sns.scatterplot(
            data=df,
            x=column,
            y=target_column,
            hue=hue,
            alpha=0.5
        )
        plt.yscale("log")
        plt.title(f"{column} vs {target_column} (échelle log)")
        plt.tight_layout()

        # Nom de fichier sûr (pas de / ni d'espace)
        safe_name = column.replace("/", "_").replace(" ", "_")
        plt.savefig(output_dir / f"target_vs_{safe_name}.png", dpi=150)
        plt.close("all")


def plot_target_by_category(
    df: pd.DataFrame,
    target_column: str,
    output_dir: Path
) -> None:
    """
    Boîtes à moustaches de la cible par type de bien et par transaction.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for column in ["type_bien", "transaction"]:
        if column not in df.columns:
            continue

        plt.figure(figsize=(10, 5))
        sns.boxplot(data=df, x=column, y=target_column)
        plt.yscale("log")
        plt.xticks(rotation=30)
        plt.title(f"{target_column} par {column} (échelle log)")
        plt.tight_layout()
        plt.savefig(output_dir / f"target_by_{column}.png", dpi=150)
        plt.close("all")


def run_eda(
    df: pd.DataFrame,
    target_column: str,
    output_dir: Path
) -> None:
    """
    Exécute les principales analyses exploratoires.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_numeric_distributions(df, output_dir)
    plot_categorical_frequencies(df, output_dir)
    plot_correlation_matrix(df, output_dir)

    if target_column in df.columns:
        plot_target_relationships(df, target_column, output_dir)
        plot_target_by_category(df, target_column, output_dir)
