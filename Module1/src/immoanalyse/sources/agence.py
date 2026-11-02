import pandas as pd
from ._common import source_path, first, record

def load(root):
    path = source_path(root, "agence_teranga.xlsx")
    df = pd.read_excel(path, sheet_name="Annonces", dtype=object)
    return [record("agence_teranga", first(r,"Code"), first(r,"Date"), None, 
                   first(r,"Type"), first(r,"Region"), first(r,"Ville"), None, 
                   first(r,"Prix_FCFA"), first(r,"Surface_m2"), first(r,"Chambres"), 
                   first(r,"SDB"), first(r,"Statut"), None) for r in df.to_dict("records")]
