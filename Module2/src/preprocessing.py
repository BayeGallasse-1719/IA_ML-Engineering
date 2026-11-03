"""
Prétraitement des variables avec scikit-learn.

Les transformations apprises sont ajustées uniquement sur train.
"""

import logging

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    DROP_COLUMNS,
    MIN_FREQUENCY,
    RANDOM_STATE,
    SCALE_NUMERIC,
    STRATIFY_COLUMN,
    TARGET_COLUMN,
    TEST_SIZE,
    VALIDATION_SIZE,
)

logger = logging.getLogger(__name__)


def split_data(
    df: pd.DataFrame
) -> tuple:
    """
    Sépare le dataset en train, validation et test.

    Les proportions de validation et de test sont définies par rapport
    au dataset total (ex. 60 % / 20 % / 20 %).

    Returns
    -------
    tuple
        X_train, X_val, X_test, y_train, y_val, y_test
    """
    if TARGET_COLUMN not in df.columns:
        raise KeyError(
            f"Variable cible absente : {TARGET_COLUMN}"
        )

    # Exclure les observations sans cible (inutilisables pour l'entraînement).
    df = df.dropna(subset=[TARGET_COLUMN]).copy()

    y = df[TARGET_COLUMN]

    # Colonnes retirées de X : la cible + les colonnes de DROP_COLUMNS
    excluded_columns = [TARGET_COLUMN] + [
        column for column in DROP_COLUMNS
        if column in df.columns
    ]

    X = df.drop(columns=excluded_columns)

    # Stratification : garde la même proportion vente/location dans chaque
    # ensemble. Désactivée si la colonne est absente, contient des
    # manquants ou a des modalités trop rares (< 3 lignes).
    stratify = None
    if STRATIFY_COLUMN and STRATIFY_COLUMN in X.columns:
        column = X[STRATIFY_COLUMN]
        if column.notna().all() and column.value_counts().min() >= 3:
            stratify = column
        else:
            logger.warning(
                "Stratification sur « %s » désactivée "
                "(manquants ou modalités trop rares).", STRATIFY_COLUMN
            )

    # 1re coupure : (train + validation) / test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify
    )

    # 2e coupure : train / validation.
    # La taille de validation est exprimée par rapport à (train + validation).
    validation_relative_size = VALIDATION_SIZE / (1 - TEST_SIZE)

    stratify_inner = (
        X_train_val[STRATIFY_COLUMN] if stratify is not None else None
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=validation_relative_size,
        random_state=RANDOM_STATE,
        stratify=stratify_inner
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    )


def build_preprocessor(
    X_train: pd.DataFrame
) -> ColumnTransformer:
    """
    Construit le préprocesseur à partir des colonnes du train.

    Les statistiques d'imputation, les paramètres du scaler et les catégories
    du OneHotEncoder seront appris lors du fit sur train.

    Numériques : imputation par la médiane (+ indicateur de valeur
    manquante), puis standardisation.
    Catégorielles : imputation par la modalité « inconnu », puis one-hot.
    """
    # Variables numériques (les booléens ne sont pas inclus par "number")
    numeric_features = X_train.select_dtypes(
        include="number"
    ).columns.tolist()

    # CORRECTION : toutes les autres colonnes sont catégorielles. Lister les
    # dtypes à la main (object, string...) ratait le dtype « str » de pandas 3
    # et les colonnes catégorielles étaient alors silencieusement supprimées.
    categorical_features = [
        column for column in X_train.columns
        if column not in numeric_features
    ]

    # --- Pipeline numérique ------------------------------------------------
    numeric_steps = [
        (
            "imputer",
            # add_indicator=True : ajoute une colonne « était manquant ».
            # Utile ici car les manquants dépendent de la source (ex. sdb).
            SimpleImputer(strategy="median", add_indicator=True)
        )
    ]

    if SCALE_NUMERIC:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(steps=numeric_steps)

    # --- Pipeline catégoriel ----------------------------------------------
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                # CORRECTION : « most_frequent » inventait un quartier pour
                # les 71 % de lignes sans quartier. Une modalité « inconnu »
                # explicite est plus honnête et informative.
                SimpleImputer(strategy="constant", fill_value="inconnu")
            ),
            (
                "encoder",
                OneHotEncoder(
                    # Modalité jamais vue en train : traitée comme « rare »
                    # au lieu de provoquer une erreur en production.
                    handle_unknown="infrequent_if_exist",
                    min_frequency=MIN_FREQUENCY,
                    sparse_output=True
                )
            )
        ]
    )

    # --- Assemblage --------------------------------------------------------
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features)
        ],
        remainder="drop"
    )

    return preprocessor
