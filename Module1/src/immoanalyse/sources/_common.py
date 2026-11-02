from pathlib import Path
import pandas as pd

CANONICAL = ["id_source", "source", "date", "transaction", "type_bien", "region", "ville", 
             "quartier", "prix_fcfa", "surface_m2", "pieces", "sdb", "statut", "description"]

def source_path(root, filename):
    root = Path(root)
    direct = root / "data" / "raw" / filename
    nested = root / "data" / "raw" / "sources" / filename
    return direct if direct.exists() else nested

def first(row, *keys):
    for key in keys:
        value = row.get(key)
        if value is not None and not pd.isna(value) and str(value).strip():
            return value
    return None

def record(source, id_source, date, transaction, type_bien, region, ville, quartier, prix, surface, pieces, sdb, statut, description=None):
    return {"id_source": id_source, "source": source, "date": date, "transaction": transaction, 
            "type_bien": type_bien, "region": region, "ville": ville, "quartier": quartier, "prix_fcfa": prix, 
            "surface_m2": surface, "pieces": pieces, "sdb": sdb, "statut": statut, "description": description}
