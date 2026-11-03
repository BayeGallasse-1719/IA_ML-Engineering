"""
Contrôles qualité des matrices après prétraitement.
"""

import numpy as np
from scipy import sparse


def validate_transformed_data(
    matrix,
    dataset_name: str,
    expected_n_features: int | None = None
) -> dict:
    """
    Vérifie la forme et la présence de valeurs non finies.

    Parameters
    ----------
    matrix : array-like ou matrice sparse
        Données transformées.
    dataset_name : str
        Nom du dataset pour les messages de contrôle.
    expected_n_features : int | None
        Nombre de colonnes attendu (celui de train). Si fourni, toute
        différence lève une erreur : train, validation et test doivent
        avoir exactement les mêmes colonnes.

    Returns
    -------
    dict
        Rapport de validation.

    Raises
    ------
    ValueError
        Si la matrice contient des NaN / infinis ou n'a pas la bonne forme.
    """
    # Pour une matrice sparse, seules les valeurs non nulles sont stockées
    # dans .data : inutile de parcourir les zéros.
    if sparse.issparse(matrix):
        values = matrix.data
    else:
        values = np.asarray(matrix).ravel()

    # np.isfinite est faux pour NaN, +inf et -inf
    non_finite_count = int((~np.isfinite(values)).sum())

    report = {
        "dataset": dataset_name,
        "shape": list(matrix.shape),
        "non_finite_count": non_finite_count,
        "is_sparse": bool(sparse.issparse(matrix)),
        "min_value": float(values.min()) if values.size else None,
        "max_value": float(values.max()) if values.size else None,
    }

    if non_finite_count > 0:
        raise ValueError(
            f"{dataset_name} contient "
            f"{non_finite_count} valeurs non finies."
        )

    if (
        expected_n_features is not None
        and matrix.shape[1] != expected_n_features
    ):
        raise ValueError(
            f"{dataset_name} a {matrix.shape[1]} colonnes, "
            f"{expected_n_features} attendues (comme train)."
        )

    return report


def check_reproducibility(preprocessor, X) -> bool:
    """
    Vérifie que deux transformations successives donnent le même résultat
    (le préprocesseur ajusté ne doit rien « apprendre » en transformant).
    """
    first = preprocessor.transform(X)
    second = preprocessor.transform(X)

    if sparse.issparse(first):
        difference = abs(first - second).sum()
    else:
        difference = np.abs(first - second).sum()

    return bool(difference == 0)
