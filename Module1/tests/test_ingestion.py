from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from immoanalyse.pipeline import load_sources, CANONICAL

class TestIngestion(unittest.TestCase):
    def test_all_sources_loaded(self):
        df = load_sources(ROOT)
        self.assertEqual(list(df.columns), CANONICAL)
        self.assertGreater(len(df), 0)
        self.assertEqual(set(df.source.unique()), {"plateforme_immo_sn", "agence_teranga", "particuliers", "notaires", "import_historique"})

if __name__ == "__main__": unittest.main()
