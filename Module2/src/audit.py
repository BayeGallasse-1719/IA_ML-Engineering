"""
Audit de qualité des données.

Ce module examine le dataset sans le modifier.
"""

import json
from pathlib import Path

import pandas as pd


def audit_dataset(
    df: pd.DataFrame,
    output_dir: Path
) -> dict:
    """
    Analyse la qualité générale du dataset.

    Produit trois fichiers dans ``output_dir`` :
    descriptive_statistics.csv, missing_values.csv et audit_report.json.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset à auditer.
    output_dir : Path
        Dossier dans lequel enregistrer les rapports.

    Returns
    -------
    dict
        Résumé de l'audit.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Valeurs manquantes : nombre et pourcentage par colonne
    missing_count = df.isna().sum()
    missing_percentage = (missing_count / len(df) * 100).round(2)

    report = {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        # Seules les colonnes réellement concernées sont conservées
        "missing_values": missing_count[missing_count > 0].to_dict(),
        "missing_percentage": (
            missing_percentage[missing_percentage > 0].to_dict()
        ),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }

    # Doublons sur l'identifiant : révèle les copies que df.duplicated() rate
    # quand seules les colonnes d'audit diffèrent (cas du Module 1).
    if "id_source" in df.columns:
        report["duplicate_ids"] = int(df["id_source"].duplicated().sum())

    # Statistiques descriptives de toutes les colonnes
    df.describe(include="all").transpose().to_csv(
        output_dir / "descriptive_statistics.csv"
    )

    # Rapport des valeurs manquantes
    missing_report = pd.DataFrame({
        "missing_count": missing_count,
        "missing_percentage": missing_percentage,
    })
    missing_report.to_csv(output_dir / "missing_values.csv")

    # Résumé JSON (default=str pour sérialiser les types numpy)
    with open(output_dir / "audit_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False, default=str)

    return report


def _iqr_stats(values: pd.Series) -> dict:
    """
    Calcule les bornes IQR et le nombre d'outliers d'une série.

    Fonction interne partagée par le cas global et le cas par groupe.
    """
    values = values.dropna()

    # Série vide : rien à analyser
    if values.empty:
        return {
            "lower_bound": float("nan"),
            "upper_bound": float("nan"),
            "n_values": 0,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
        }

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = (values < lower_bound) | (values > upper_bound)

    return {
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "n_values": int(len(values)),
        "outlier_count": int(outliers.sum()),
        "outlier_percentage": round(outliers.mean() * 100, 2),
    }


def detect_outliers_iqr(
    df: pd.DataFrame,
    columns: list[str],
    group_columns: list[str] | None = None
) -> pd.DataFrame:
    """
    Détecte les valeurs aberrantes avec la méthode IQR.

    La fonction signale les anomalies sans supprimer les observations.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset à examiner.
    columns : list[str]
        Colonnes numériques à analyser.
    group_columns : list[str] | None
        Si fourni, l'analyse est faite séparément pour chaque groupe
        (ex. ["type_bien", "transaction"]). Indispensable ici : comparer le
        prix d'un terrain à celui d'une villa, ou une location à une vente,
        n'a pas de sens.

    Returns
    -------
    pd.DataFrame
        Tableau contenant les bornes et le nombre d'outliers par variable
        (et par groupe le cas échéant).
    """
    results = []

    for column in columns:
        if group_columns:
            # Une analyse IQR par combinaison de modalités
            for keys, group in df.groupby(group_columns, dropna=False):
                keys = keys if isinstance(keys, tuple) else (keys,)
                row = {"column": column}
                row.update(dict(zip(group_columns, keys)))
                row.update(_iqr_stats(group[column]))
                results.append(row)
        else:
            row = {"column": column}
            row.update(_iqr_stats(df[column]))
            results.append(row)

    return pd.DataFrame(results)
