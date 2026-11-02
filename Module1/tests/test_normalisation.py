from pathlib import Path
import sys, unittest, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from immoanalyse.normalisation import parse_number, parse_date, clean_text
class TestNormalisation(unittest.TestCase):
    def test_price_millions(self): self.assertEqual(parse_number("2,5 millions FCFA", "prix"), 2500000)
    def test_thousands(self): self.assertEqual(parse_number("1 250 000", "prix"), 1250000)
    def test_date_fr(self): self.assertEqual(parse_date("31/12/2024"), pd.Timestamp("2024-12-31"))
    def test_empty_text(self): self.assertIsNone(clean_text("  "))
if __name__ == "__main__": unittest.main()
