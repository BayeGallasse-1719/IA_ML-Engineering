import sys
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from immoanalyse.pipeline import parse_number, parse_date, clean_text, norm_label, normalize, validate, detect_duplicates

class TestNettoyage(unittest.TestCase):
    def test_prix_avec_espaces(self):
        self.assertEqual(parse_number("26 620 000", "prix"), 26620000)
    def test_prix_millions(self):
        self.assertEqual(parse_number("12,5 millions FCFA", "prix"), 12500000)
    def test_surface_virgule_decimale(self):
        self.assertAlmostEqual(parse_number("44,7", "surface"), 44.7)
    def test_date_francaise(self):
        self.assertEqual(parse_date("11/05/2022"), pd.Timestamp("2022-05-11"))
    def test_date_invalide(self):
        self.assertTrue(pd.isna(parse_date("32/13/2024")))
    def test_espaces(self):
        self.assertEqual(clean_text("  Dakar   Plateau "), "Dakar Plateau")
    def test_casse(self):
        self.assertEqual(norm_label("  dAKAR "), "Dakar")
    def test_pipeline_charge_les_cinq_sources(self):
        from immoanalyse.pipeline import load_sources
        data = load_sources(ROOT)
        self.assertEqual(set(data.source.unique()), {"plateforme_immo_sn", "agence_teranga", "particuliers", "notaires", "import_historique"})
        self.assertGreater(len(data), 0)

if __name__ == "__main__":
    unittest.main()
