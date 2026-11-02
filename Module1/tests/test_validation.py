from pathlib import Path
import sys, unittest, pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from immoanalyse.pipeline import validate
class TestValidation(unittest.TestCase):
    def test_missing_price_quarantined(self):
        df=pd.DataFrame([{"id_source":"X1","date":pd.Timestamp("2024-01-01"),"prix_fcfa":float("nan"),"surface_m2":40,"statut":"En vente","geo_incoherente":False,"type_inconnu":False,"doublon_probable":False,"doublon_exact":False}])
        # Complète le schéma attendu par la règle de validation
        for c in ["source","transaction","type_bien","region","ville","quartier","pieces","sdb","description"]:
            if c not in df: df[c]=None
        out=validate(df,today="2025-01-01")
        self.assertEqual(out.loc[0,"decision"],"quarantaine")
        self.assertIn("prix_absent_ou_invalide",out.loc[0,"motifs_quarantaine"])
if __name__ == "__main__": unittest.main()
