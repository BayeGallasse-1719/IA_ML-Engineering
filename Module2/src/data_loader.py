"""
Chargement des données nettoyées dans le Module 1.

Ce module prend en charge les formats CSV et Parquet.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Charge le dataset préparé au Module 1.

    Parameters
    ----------
    file_path : Path
        Chemin vers le fichier de données (.csv, .parquet ou .pq).

    Returns
    -------
    pd.DataFrame
        Dataset chargé en mémoire.

    Raises
    ------
    FileNotFoundError
        Si le fichier n'existe pas.
    ValueError
        Si le format n'est pas pris en charge.
    """
    # Vérification de l'existence du fichier avant toute lecture
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    extension = file_path.suffix.lower()

    if extension == ".csv":
        # utf-8-sig : le CSV du Module 1 commence par un BOM (caractère invisible)
        # qui, sinon, se retrouve collé au nom de la première colonne.
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    elif extension in {".parquet", ".pq"}:
        df = pd.read_parquet(file_path)
    else:
        raise ValueError("Format accepté : CSV ou Parquet.")

    # Nettoyage des espaces parasites dans les noms de colonnes
    df.columns = df.columns.str.strip()

    logger.info("Dataset chargé : %s lignes, %s colonnes", *df.shape)

    return df
