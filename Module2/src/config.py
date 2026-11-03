"""
Configuration centrale du Module 2.

Tous les chemins, noms de colonnes et paramètres du projet sont définis ici.
Modifier ce fichier suffit pour adapter le pipeline à un autre dataset.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

# Racine du projet : dossier parent de src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Données d'entrée issues du Module 1.
# CORRECTION : l'ancien chemin (data/processed/immo_module_01_clean.csv)
# n'existait pas ; le fichier réel est data/raw/donnees_propres.csv.
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "donnees_propres.csv"

# Dataset nettoyé + enrichi, exporté par le Module 2
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_DATA_PATH = PROCESSED_DATA_DIR / "immo_module_02_clean.csv"

# Dossiers de rapports
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
AUDIT_DIR = REPORTS_DIR / "audit"

# Dossiers d'artefacts (matrices transformées et pipeline sérialisé)
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
TRANSFORMED_DATA_DIR = ARTIFACTS_DIR / "data"
PIPELINES_DIR = ARTIFACTS_DIR / "pipelines"

# ---------------------------------------------------------------------------
# Variable cible et colonnes à exclure
# ---------------------------------------------------------------------------

# Variable cible à prédire
TARGET_COLUMN = "prix_fcfa"

# Colonnes retirées de X avant le prétraitement.
# Justification de chaque exclusion :
#   - id_source        : identifiant, aucune valeur prédictive (risque de mémorisation)
#   - description      : texte généré à partir du type et de la ville (redondant)
#   - doublon_*        : drapeaux d'audit du Module 1, pas des caractéristiques du bien
#   - avertissements,
#     decision         : sorties du contrôle qualité du Module 1 (méta-information)
#   - statut           : résultat de la vie de l'annonce (vendu, loué...), non connu
#                        au moment de la prédiction ; sert uniquement à compléter
#                        la colonne « transaction » (voir anomalies.py)
#   - source           : artefact de collecte, pas une caractéristique du bien
#   - date             : remplacée par listing_year / listing_month (feature engineering)
DROP_COLUMNS = [
    "id_source",
    "description",
    "doublon_exact",
    "doublon_probable",
    "avertissements",
    "decision",
    "statut",
    "source",
    "date",
]

# ---------------------------------------------------------------------------
# Découpage des données
# ---------------------------------------------------------------------------

TEST_SIZE = 0.20          # 20 % du dataset total pour le test
VALIDATION_SIZE = 0.20    # 20 % du dataset total pour la validation
RANDOM_STATE = 42         # Graine pour la reproductibilité

# Colonne utilisée pour stratifier le split (vente et location ont des prix
# 1000 fois différents : chaque ensemble doit contenir les deux en proportion
# identique). Mettre None pour désactiver.
STRATIFY_COLUMN = "transaction"

# ---------------------------------------------------------------------------
# Prétraitement
# ---------------------------------------------------------------------------

SCALE_NUMERIC = True      # Standardisation des variables numériques
MIN_FREQUENCY = 2         # Modalités rares regroupées dans « infrequent »

# ---------------------------------------------------------------------------
# Noms de colonnes du dataset (adapter si le dataset change)
# CORRECTION : ROOMS_COLUMN valait "rooms" alors que la colonne s'appelle "pieces".
# ---------------------------------------------------------------------------

SURFACE_COLUMN = "surface_m2"
ROOMS_COLUMN = "pieces"
BATHROOMS_COLUMN = "sdb"
TYPE_COLUMN = "type_bien"
TRANSACTION_COLUMN = "transaction"
STATUS_COLUMN = "statut"
DATE_COLUMN = "date"          # CORRECTION : était None alors que la colonne existe
LOCATION_COLUMN = "region"    # Utilisée pour l'indicateur « Dakar »

# ---------------------------------------------------------------------------
# Règles de traitement des anomalies
# ---------------------------------------------------------------------------

# Toute date postérieure est considérée invalide (le dataset contient des 2028)
MAX_VALID_DATE = "2026-12-31"

# Types de biens pour lesquels 0 pièce est une valeur légitime
TYPES_WITHOUT_ROOMS = ["terrain", "local commercial"]

# Colonnes d'audit ignorées lors de la détection des doublons
AUDIT_FLAG_COLUMNS = [
    "doublon_exact",
    "doublon_probable",
    "avertissements",
    "decision",
]

# Déduction de la transaction manquante à partir du statut de l'annonce.
# Règle observée sur les lignes où les deux colonnes sont renseignées :
# « Loué » et « Disponible » -> location ; tous les autres statuts -> vente.
STATUS_TO_TRANSACTION = {
    "vendu": "vente",
    "vente conclue": "vente",
    "acte signé": "vente",
    "en vente": "vente",
    "sous offre": "vente",
    "retiré": "vente",
    "à confirmer": "vente",
    "loué": "location",
    "disponible": "location",
}
