import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit import detect_outliers_iqr
from src.config import (
    AUDIT_FLAG_COLUMNS,
    BATHROOMS_COLUMN,
    DATE_COLUMN,
    MAX_VALID_DATE,
    ROOMS_COLUMN,
    STATUS_COLUMN,
    STATUS_TO_TRANSACTION,
    SURFACE_COLUMN,
    TARGET_COLUMN,
    TRANSACTION_COLUMN,
    TYPE_COLUMN,
    TYPES_WITHOUT_ROOMS,
)

logger = logging.getLogger(__name__)


def handle_anomalies(
    df: pd.DataFrame,
    output_dir: Path
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Détecte et traite les anomalies du dataset.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    result = df.copy()
    decisions: list[dict] = []

    def log_decision(anomalie: str, action: str, n: int, justification: str):
        """Enregistre une décision (et l'affiche dans les logs)."""
        decisions.append({
            "anomalie": anomalie,
            "action": action,
            "lignes_concernees": int(n),
            "justification": justification,
        })
        logger.info("Anomalie « %s » : %s (%s lignes)", anomalie, action, n)

    # -----------------------------------------------------------------
    # 1. Normalisation du texte (espaces parasites, casse du statut)
    # -----------------------------------------------------------------
    text_columns = result.select_dtypes(exclude=["number", "bool"]).columns
    for column in text_columns:
        result[column] = result[column].str.strip()

    if STATUS_COLUMN in result.columns:
        before = result[STATUS_COLUMN].copy()
        # capitalize() : 1re lettre en majuscule, le reste en minuscule
        result[STATUS_COLUMN] = result[STATUS_COLUMN].str.capitalize()
        n_changed = int((before != result[STATUS_COLUMN]).sum())
        log_decision(
            "Casse incohérente du statut",
            "corriger",
            n_changed,
            "Même modalité écrite de deux façons : harmonisation de la casse."
        )

    # -----------------------------------------------------------------
    # 2. Doublons exacts
    # -----------------------------------------------------------------
    business_columns = [
        c for c in result.columns if c not in AUDIT_FLAG_COLUMNS
    ]
    duplicate_mask = result.duplicated(subset=business_columns, keep="first")
    n_duplicates = int(duplicate_mask.sum())
    result = result.loc[~duplicate_mask].copy()
    log_decision(
        "Doublons exacts (même annonce répétée)",
        "exclure (on garde la première occurrence)",
        n_duplicates,
        "Une copie identique pourrait se retrouver à la fois dans train et "
        "test et fausser l'évaluation (fuite d'information)."
    )

    # -----------------------------------------------------------------
    # 3. Dates invalides (ex. année 2028, impossible pour une annonce passée)
    #    On invalide la date mais on GARDE la ligne : le reste est exploitable.
    # -----------------------------------------------------------------
    if DATE_COLUMN in result.columns:
        dates = pd.to_datetime(result[DATE_COLUMN], errors="coerce")
        invalid_dates = dates > pd.Timestamp(MAX_VALID_DATE)
        n_invalid = int(invalid_dates.sum())
        dates = dates.mask(invalid_dates)  # remplace par NaT
        result[DATE_COLUMN] = dates
        log_decision(
            "Dates dans le futur",
            "corriger (date -> manquante, ligne conservée)",
            n_invalid,
            f"Dates postérieures à {MAX_VALID_DATE} : invalides. "
            "La valeur manquante sera imputée dans le pipeline."
        )

    # -----------------------------------------------------------------
    # 4. Nombre de pièces = 0 pour un bien qui devrait en avoir
    #    (0 est légitime pour un terrain ou un local commercial)
    # -----------------------------------------------------------------
    if ROOMS_COLUMN in result.columns and TYPE_COLUMN in result.columns:
        zero_rooms = (
            (result[ROOMS_COLUMN] == 0)
            & ~result[TYPE_COLUMN].isin(TYPES_WITHOUT_ROOMS)
        )
        n_zero = int(zero_rooms.sum())
        result.loc[zero_rooms, ROOMS_COLUMN] = np.nan
        log_decision(
            "0 pièce pour un logement (appartement, maison, villa...)",
            "corriger (pièces -> manquant, ligne conservée)",
            n_zero,
            "Valeur impossible pour un logement ; imputée par la médiane "
            "dans le pipeline."
        )

    # -----------------------------------------------------------------
    # 5. Transaction manquante
    # -----------------------------------------------------------------
    if TRANSACTION_COLUMN in result.columns and STATUS_COLUMN in result.columns:
        missing = result[TRANSACTION_COLUMN].isna()
        inferred = (
            result.loc[missing, STATUS_COLUMN]
            .str.lower()
            .map(STATUS_TO_TRANSACTION)
        )
        result.loc[missing, TRANSACTION_COLUMN] = inferred
        n_filled = int(inferred.notna().sum())
        log_decision(
            "Transaction manquante (vente / location)",
            "corriger (déduite du statut de l'annonce)",
            n_filled,
            "Règle statut -> transaction vérifiée sur les lignes complètes. "
            "Le prix n'est pas utilisé (évite la fuite de la cible)."
        )

    # -----------------------------------------------------------------
    # 6. Anomalies signalées par le Module 1 : on CONSERVE
    # -----------------------------------------------------------------
    if "avertissements" in result.columns:
        warnings = result["avertissements"].fillna("")

        n_price = int(warnings.str.contains("prix_atypique").sum())
        log_decision(
            "Prix atypiques signalés par le Module 1",
            "conserver",
            n_price,
            "Prix bas mais plausibles (ex. terrain en zone rurale, chambre "
            "bon marché) : les supprimer biaiserait le modèle vers les "
            "biens chers. Mesure de robustesse conseillée : transformer la "
            "cible en logarithme au Module 3."
        )

        n_geo = int(
            warnings.str.contains("ville_region_incompatible").sum()
        )
        log_decision(
            "Ville incompatible avec la région",
            "conserver",
            n_geo,
            "Quelques lignes seulement, probablement un découpage "
            "administratif différent ; impact négligeable."
        )

    # -----------------------------------------------------------------
    # 7. Valeurs aberrantes statistiques (IQR) : on SIGNALE, on ne supprime pas.
    #    L'analyse est faite PAR TYPE DE BIEN ET PAR TRANSACTION, sinon un
    #    terrain ou une location serait « aberrant » à cause de son groupe.
    # -----------------------------------------------------------------
    numeric_to_check = [
        c for c in [TARGET_COLUMN, SURFACE_COLUMN]
        if c in result.columns
    ]
    group_columns = [
        c for c in [TYPE_COLUMN, TRANSACTION_COLUMN]
        if c in result.columns
    ]

    if numeric_to_check:
        outliers = detect_outliers_iqr(
            result, numeric_to_check, group_columns or None
        )
        outliers.to_csv(output_dir / "outliers_iqr.csv", index=False)

        log_decision(
            "Valeurs aberrantes IQR (prix, surface) par type et transaction",
            "conserver (signalées dans outliers_iqr.csv)",
            int(outliers["outlier_count"].sum()),
            "Valeurs extrêmes mais réalistes (grandes villas, grands "
            "terrains). Pas de suppression automatique sans justification "
            "métier ; les modèles à base d'arbres y sont peu sensibles."
        )

    # -----------------------------------------------------------------
    # 8. Valeurs manquantes structurelles (sdb, quartier, ville) : on conserve.
    #    Elles dépendent de la source (ex. les notaires ne renseignent jamais
    #    « sdb »). Le pipeline les imputera et ajoutera un indicateur.
    # -----------------------------------------------------------------
    for column in [BATHROOMS_COLUMN, "quartier", "ville"]:
        if column in result.columns:
            n_missing = int(result[column].isna().sum())
            log_decision(
                f"Valeurs manquantes dans « {column} »",
                "conserver (imputation dans le pipeline)",
                n_missing,
                "Manquants liés à la source des données, pas à une erreur ; "
                "l'imputation est apprise sur train uniquement."
            )

    # Journal des décisions
    with open(
        output_dir / "anomaly_decisions.json", "w", encoding="utf-8"
    ) as file:
        json.dump(decisions, file, indent=4, ensure_ascii=False)

    return result, decisions
