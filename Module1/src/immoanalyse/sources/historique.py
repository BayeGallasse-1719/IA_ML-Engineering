import pandas as pd
from ._common import source_path, first, record

def load(root):
    path = source_path(root, "import_historique.csv")
    # Fichier historique historiquement encodé en Latin-1 et séparé par point-virgule.
    df = pd.read_csv(path, sep=";", dtype=object, encoding="latin-1")
    return [record("import_historique", first(r,"ID"), first(r,"DateVente"), "vente", first(r,"TypeBien"), 
                   first(r,"Region"), first(r,"Ville"), None, first(r,"Prix"), first(r,"Surface"), 
                   first(r,"Chambres"), first(r,"SallesBain"), "Vendu", None) for r in df.to_dict("records")]
