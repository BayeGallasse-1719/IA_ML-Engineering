from pathlib import Path
import sys
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from immoanalyse.pipeline import normalize, CANONICAL

class TestGeographie(unittest.TestCase):
    def test_valeurs_geographiques_manquantes_ne_font_pas_planter(self):
        row = {col: None for col in CANONICAL}
        row.update({"id_source": "TEST-1", "source": "test", "region": float("nan"),
                    "ville": "Dakar", "type_bien": "Villa", "date": "2024-01-01",
                    "prix_fcfa": 10000000, "surface_m2": 100})
        normalized, _ = normalize(pd.DataFrame([row]), ROOT)
        self.assertFalse(bool(normalized.loc[0, "geo_incoherente"]))

if __name__ == "__main__":
    unittest.main()
