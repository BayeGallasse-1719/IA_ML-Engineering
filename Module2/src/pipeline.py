"""
Orchestration complète du Module 2.

Ce module exécute, dans l'ordre :
1. Chargement des données.
2. Audit.
3. EDA.
4. Traitement des anomalies.
5. Feature Engineering.
6. Split train / validation / test.
7. Prétraitement (fit sur train uniquement).
8. Validation qualité.
9. Export (données, pipeline, rapports).
"""

import json
import logging

import joblib
import numpy as np
from scipy import sparse

from src.anomalies import handle_anomalies
from src.audit import audit_dataset
from src.config import (
    AUDIT_DIR,
    CLEAN_DATA_PATH,
    DATA_PATH,
    FIGURES_DIR,
    PIPELINES_DIR,
    PROCESSED_DATA_DIR,
    TARGET_COLUMN,
    TRANSFORMED_DATA_DIR,
)
from src.data_loader import load_dataset
from src.eda import run_eda
from src.feature_engineering import engineer_features
from src.preprocessing import build_preprocessor, split_data
from src.validation import check_reproducibility, validate_transformed_data

logger = logging.getLogger(__name__)


def save_matrix(matrix, file_path):
    """
    Sauvegarde une matrice dense ou sparse.

    Les matrices sparse sont stockées au format NPZ.
    Les matrices denses sont stockées au format NPY.
    """
    if sparse.issparse(matrix):
        sparse.save_npz(file_path.with_suffix(".npz"), matrix)
    else:
        np.save(file_path.with_suffix(".npy"), matrix)


def run_module_02():
    """
    Exécute l'intégralité du workflow de préparation.
    """
    # ---------------------------------------------------------
    # 1. Chargement des données
    # ---------------------------------------------------------
    logger.info("Chargement du dataset...")
    df = load_dataset(DATA_PATH)

    # ---------------------------------------------------------
    # 2. Audit initial (sur les données brutes, sans modification)
    # ---------------------------------------------------------
    logger.info("Audit des données...")
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_dataset(df, AUDIT_DIR)

    # ---------------------------------------------------------
    # 3. Analyse exploratoire (sur les données brutes)
    # ---------------------------------------------------------
    logger.info("Analyse exploratoire...")
    run_eda(df, TARGET_COLUMN, FIGURES_DIR)

    # ---------------------------------------------------------
    # 4. Traitement des anomalies
    #    (étape 3 du plan : absente du pipeline d'origine)
    # ---------------------------------------------------------
    logger.info("Traitement des anomalies...")
    df, _ = handle_anomalies(df, AUDIT_DIR)

    # ---------------------------------------------------------
    # 5. Feature Engineering
    # ---------------------------------------------------------
    logger.info("Feature Engineering...")
    df = engineer_features(df)

    # Export du dataset nettoyé et enrichi (data/processed)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DATA_PATH, index=False, encoding="utf-8-sig")

    # ---------------------------------------------------------
    # 6. Split des données (avant tout fit : évite la fuite d'information)
    # ---------------------------------------------------------
    logger.info("Séparation train / validation / test...")
    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    ) = split_data(df)

    logger.info(
        "Tailles : train=%s, validation=%s, test=%s",
        len(X_train), len(X_val), len(X_test)
    )

    # ---------------------------------------------------------
    # 7. Construction et ajustement du préprocesseur
    # ---------------------------------------------------------
    logger.info("Construction du préprocesseur...")
    preprocessor = build_preprocessor(X_train)

    # fit_transform sur train UNIQUEMENT : médianes, moyennes, écarts-types
    # et catégories sont appris ici.
    logger.info("Ajustement du préprocesseur sur train...")
    X_train_transformed = preprocessor.fit_transform(X_train)

    # Validation et test : transform uniquement (aucun apprentissage).
    X_val_transformed = preprocessor.transform(X_val)
    X_test_transformed = preprocessor.transform(X_test)

    # ---------------------------------------------------------
    # 8. Validation qualité
    # ---------------------------------------------------------
    logger.info("Validation des données transformées...")

    n_features = X_train_transformed.shape[1]

    quality_reports = [
        validate_transformed_data(X_train_transformed, "train", n_features),
        validate_transformed_data(X_val_transformed, "validation", n_features),
        validate_transformed_data(X_test_transformed, "test", n_features),
    ]

    # Le même résultat doit sortir à chaque appel de transform
    reproducible = check_reproducibility(preprocessor, X_val)
    if not reproducible:
        raise ValueError("Le préprocesseur n'est pas reproductible.")

    quality_reports.append({"reproducibility_check": reproducible})

    # ---------------------------------------------------------
    # 9. Export des matrices, cibles et indices du split
    # ---------------------------------------------------------
    logger.info("Export des données...")
    TRANSFORMED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    save_matrix(X_train_transformed, TRANSFORMED_DATA_DIR / "X_train")
    save_matrix(X_val_transformed, TRANSFORMED_DATA_DIR / "X_validation")
    save_matrix(X_test_transformed, TRANSFORMED_DATA_DIR / "X_test")

    # Export des cibles (même ordre de lignes que les matrices X)
    y_train.to_frame(TARGET_COLUMN).to_csv(
        TRANSFORMED_DATA_DIR / "y_train.csv", index=False
    )
    y_val.to_frame(TARGET_COLUMN).to_csv(
        TRANSFORMED_DATA_DIR / "y_validation.csv", index=False
    )
    y_test.to_frame(TARGET_COLUMN).to_csv(
        TRANSFORMED_DATA_DIR / "y_test.csv", index=False
    )

    # Noms des colonnes de la matrice transformée (interprétation du modèle)
    feature_names = preprocessor.get_feature_names_out().tolist()
    with open(
        TRANSFORMED_DATA_DIR / "feature_names.json", "w", encoding="utf-8"
    ) as file:
        json.dump(feature_names, file, indent=4, ensure_ascii=False)

    # Indices des lignes de chaque ensemble : le split est ainsi traçable
    with open(
        TRANSFORMED_DATA_DIR / "split_indices.json", "w", encoding="utf-8"
    ) as file:
        json.dump(
            {
                "train": X_train.index.tolist(),
                "validation": X_val.index.tolist(),
                "test": X_test.index.tolist(),
            },
            file
        )

    # ---------------------------------------------------------
    # 10. Sauvegarde du pipeline ajusté
    # ---------------------------------------------------------
    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        preprocessor,
        PIPELINES_DIR / "preprocessing_pipeline.joblib"
    )

    # ---------------------------------------------------------
    # 11. Rapport qualité
    # ---------------------------------------------------------
    with open(
        AUDIT_DIR / "transformed_quality.json", "w", encoding="utf-8"
    ) as file:
        json.dump(quality_reports, file, indent=4, ensure_ascii=False)

    logger.info("Module 2 terminé avec succès.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    run_module_02()
