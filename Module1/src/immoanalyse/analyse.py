"""Outils d'analyse descriptive et de profilage."""
from pathlib import Path
import pandas as pd

def profil_qualite(df: pd.DataFrame) -> dict:
    """Retourne un profil synthétique réutilisable dans les notebooks."""
    return {"lignes": int(len(df)), "colonnes": int(len(df.columns)), 
            "valeurs_manquantes": df.isna().sum().astype(int).to_dict(), 
            "lignes_dupliquees": int(df.duplicated().sum())}

def resume_prix(df: pd.DataFrame) -> pd.DataFrame:
    """Statistiques de prix FCFA par type de bien, sur données nettoyées."""
    if not {"type_bien", "prix_fcfa"}.issubset(df.columns):
        raise ValueError("Les colonnes type_bien et prix_fcfa sont requises")
    work = df.copy()
    work["prix_fcfa"] = pd.to_numeric(work["prix_fcfa"], errors="coerce")
    return work.groupby("type_bien", dropna=False)["prix_fcfa"].agg(["count", "median", "mean", "min", "max"]).reset_index()
