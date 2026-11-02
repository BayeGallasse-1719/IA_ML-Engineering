from pathlib import Path
import sys, unittest, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from immoanalyse.deduplication import detect_duplicates
class TestDeduplication(unittest.TestCase):
    def test_exact_duplicate(self):
        df=pd.DataFrame([{"date":pd.Timestamp("2024-01-01"),"ville":"Dakar","type_bien":"villa","prix_fcfa":10000000,"surface_m2":100,"source":"a"},{"date":pd.Timestamp("2024-01-01"),"ville":"Dakar","type_bien":"villa","prix_fcfa":10000000,"surface_m2":100,"source":"b"}])
        out=detect_duplicates(df)
        self.assertEqual(int(out.doublon_exact.sum()),1)
if __name__ == "__main__": unittest.main()
