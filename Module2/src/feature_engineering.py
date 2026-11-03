"""
Feature Engineering métier.

Ajouter ici les transformations spécifiques au dataset immobilier.
"""

import numpy as np
import pandas as pd

from src.config import (
    DATE_COLUMN,
    LOCATION_COLUMN,
    ROOMS_COLUMN,
    SURFACE_COLUMN,
)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée de nouvelles variables explicatives.

    Variables créées (dictionnaire des features) :

    - ``surface_per_room`` : surface moyenne par pièce (m²/pièce).
    - ``listing_year``     : année de publication de l'annonce.
    - ``listing_month``    : mois de publication (saisonnalité).
    - ``is_dakar``         : 1 si le bien est dans la région de Dakar
      (marché immobilier très différent du reste du pays).

    Parameters
    ----------
    df : pd.DataFrame
        Dataset d'entrée (après traitement des anomalies).

    Returns
    -------
    pd.DataFrame
        Dataset enrichi.

    Notes
    -----
    Ne pas créer de features utilisant directement la cible.
    Exemple volontairement NON créé : le « prix au m² » (prix / surface),
    car il contient la cible et provoquerait une fuite de données.
    Les transformations apprenant des statistiques (moyennes, médianes...)
    doivent être intégrées au pipeline scikit-learn après le split.
    """
    result = df.copy()

    # --- Surface moyenne par pièce ----------------------------------------
    if (
        SURFACE_COLUMN in result.columns
        and ROOMS_COLUMN in result.columns
    ):
        surface = pd.to_numeric(result[SURFACE_COLUMN], errors="coerce")
        rooms = pd.to_numeric(result[ROOMS_COLUMN], errors="coerce")

        # CORRECTION : l'ancien code utilisait pd.NA, qui transforme la
        # colonne en type « object » (le pipeline ne la reconnaissait plus
        # comme numérique). np.nan garde un type float.
        result["surface_per_room"] = surface / rooms.replace(0, np.nan)

    # --- Variables temporelles --------------------------------------------
    if DATE_COLUMN and DATE_COLUMN in result.columns:
        dates = pd.to_datetime(result[DATE_COLUMN], errors="coerce")

        result["listing_year"] = dates.dt.year
        result["listing_month"] = dates.dt.month

    # --- Variable géographique --------------------------------------------
    if LOCATION_COLUMN and LOCATION_COLUMN in result.columns:
        result["is_dakar"] = (
            result[LOCATION_COLUMN].eq("Dakar").astype(int)
        )

    return result
