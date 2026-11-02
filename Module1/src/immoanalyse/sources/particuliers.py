import json
from ._common import source_path, record

def load(root):
    with open(source_path(root, "particuliers.json"), encoding="utf-8") as fh:
        payload = json.load(fh)
    records = []
    for obj in payload:
        a = obj.get("annonce", obj)
        loc, det = a.get("localisation", {}) or {}, a.get("details", {}) or {}
        records.append(record("particuliers", a.get("id"), a.get("date"), det.get("transaction"), 
                              det.get("type"), loc.get("region"), loc.get("ville"), loc.get("quartier"), 
                              det.get("prix"), det.get("surface"), det.get("chambres"), det.get("sdb"), 
                              a.get("statut"), a.get("description")))
    return records
