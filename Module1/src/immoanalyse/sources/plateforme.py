import pandas as pd
from ._common import source_path, first, record

def load(root):
    path = source_path(root, "plateforme_immo_sn.csv")
    df = pd.read_csv(path, sep=";", dtype=object, encoding="utf-8-sig")
    return [record("plateforme_immo_sn", first(r,"ref_plateforme"), first(r,"date_mise_en_ligne"), 
                   first(r,"type_transaction"), first(r,"categorie"), first(r,"region"), first(r,"commune"), 
                   first(r,"quartier"), first(r,"prix"), first(r,"surface"), first(r,"pieces"), first(r,"sdb"), 
                   first(r,"statut"), first(r,"description")) for r in df.to_dict("records")]
