import pandas as pd
from ._common import source_path, first, record

def load(root):
    path = source_path(root, "notaires.csv")
    df = pd.read_csv(path, sep=",", dtype=object, encoding="utf-8-sig")
    return [record("notaires", first(r,"id_acte"), first(r,"date_acte"), "vente", 
                   first(r,"type_bien"), first(r,"region"), first(r,"ville"), None, 
                   first(r,"montant_fcfa"), first(r,"superficie"), first(r,"nb_chambres"), None, 
                   first(r,"statut"), None) for r in df.to_dict("records")]
