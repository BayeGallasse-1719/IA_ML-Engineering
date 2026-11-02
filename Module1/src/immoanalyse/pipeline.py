from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

import pandas as pd

CANONICAL = ["id_source", "source", "date", "transaction", "type_bien", "region", "ville", 
             "quartier", "prix_fcfa", "surface_m2", "pieces", "sdb", "statut", "description"]


def clean_text(value):
    if pd.isna(value) or value is None:
        return None
    s = re.sub(r"\s+", " ", str(value)).strip()
    return s or None


def norm_label(value):
    s = clean_text(value)
    if not s:
        return None
    return s.title()


def parse_number(value, field="number"):
    """Convertit un nombre avec séparateurs français/espaces et unités explicites.

    Pour les prix, les suffixes 'million(s)' sont pris en charge. Les valeurs
    ambiguës ne sont pas devinées : elles produisent NaN et seront quarantainées.
    """
    if value is None or pd.isna(value):
        return float("nan")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip().lower().replace("\u00a0", " ").replace("fcfa", "").replace("f cfa", "").strip()
    if not s:
        return float("nan")
    multiplier = 1
    if field == "prix" and re.search(r"\b(millions?|m)\b", s):
        multiplier = 1_000_000
        s = re.sub(r"\b(millions?|m)\b", "", s).strip()
    s = re.sub(r"\s+", "", s)
    # Un point ou une virgule suivis de 1-2 chiffres sont décimaux; sinon séparateurs milliers.
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        tail = s.rsplit(",", 1)[1]
        s = s.replace(",", ".") if len(tail) in (1, 2) else s.replace(",", "")
    elif "." in s:
        tail = s.rsplit(".", 1)[1]
        if len(tail) == 3 and s.count(".") == 1:
            s = s.replace(".", "")
    s = re.sub(r"[^0-9+\-.]", "", s)
    try:
        return float(s) * multiplier
    except (ValueError, TypeError):
        return float("nan")


def parse_date(value):
    if value is None or pd.isna(value) or not str(value).strip():
        return pd.NaT
    if isinstance(value, (pd.Timestamp, datetime)):
        return pd.Timestamp(value).normalize()
    s = str(value).strip()
    # dayfirst gère JJ/MM/AAAA; ISO est également reconnu.
    try:
        # ISO d'abord pour éviter toute ambiguïté et les avertissements pandas.
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return pd.Timestamp(datetime.strptime(s, "%Y-%m-%d")).normalize()
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
            return pd.Timestamp(datetime.strptime(s, "%d/%m/%Y")).normalize()
        return pd.to_datetime(s, dayfirst=True, errors="raise").normalize()
    except (ValueError, TypeError, OverflowError):
        return pd.NaT


def _first(row, *keys):
    for k in keys:
        if k in row and not pd.isna(row[k]) and str(row[k]).strip():
            return row[k]
    return None


def _record(row, source, id_value, date, transaction, type_bien, region, ville, quartier,
            prix, surface, pieces, sdb, statut, description=None):
    return {"id_source": clean_text(id_value), "source": source,
            "date": date, "transaction": clean_text(transaction),
            "type_bien": clean_text(type_bien), "region": clean_text(region),
            "ville": clean_text(ville), "quartier": clean_text(quartier),
            "prix_fcfa": prix, "surface_m2": surface, "pieces": pieces,
            "sdb": sdb, "statut": clean_text(statut), "description": clean_text(description)}


def load_sources(root: Path) -> pd.DataFrame:
    """Charge les cinq sources via leurs adaptateurs dédiés et retourne le schéma canonique."""
    from .sources import plateforme, agence, particuliers, notaires, historique
    records = []
    for adapter in (plateforme, agence, particuliers, notaires, historique):
        records.extend(adapter.load(root))
    return pd.DataFrame(records, columns=CANONICAL)


def normalize(df: pd.DataFrame, root: Path) -> tuple[pd.DataFrame, dict]:
    out = df.copy()
    stats = {"conversions_echouees": {}}
    out["id_source"] = out["id_source"].map(clean_text)
    for c in ["region", "ville", "quartier"]:
        out[c] = out[c].map(norm_label)
    out["type_bien"] = out["type_bien"].map(lambda x: clean_text(x).casefold() if clean_text(x) else None)
    synonyms = {"appart":"appartement", "appt":"appartement", "appartement":"appartement",
                "maison":"maison", "villa":"villa", "studio":"studio", "terrain":"terrain",
                "terrains":"terrain", "chambre simple":"chambre", "chambre":"chambre",
                "local":"local commercial", "bureau":"local commercial", "magasin":"local commercial",
                "local commercial":"local commercial"}
    out["type_bien"] = out["type_bien"].map(lambda x: synonyms.get(x, x.title() if x else None))
    out["date"] = out["date"].map(parse_date)
    for c, fld in [("prix_fcfa","prix"),("surface_m2","surface"),("pieces","number"),("sdb","number")]:
        before = out[c].copy()
        out[c] = out[c].map(lambda x: parse_number(x, fld))
        stats["conversions_echouees"][c] = int((before.notna() & out[c].isna()).sum())
    # Référentiel catégories et géographie: utilisé pour avertir, pas pour inventer/corriger.
    cat_path = Path(root)/"data"/"raw"/"referentiels"/"referentiel_categories.csv"
    if cat_path.exists():
        cats = pd.read_csv(cat_path)
        known_types = set(cats["categorie"].dropna().astype(str).str.casefold())
    else: known_types = set()
    out["type_inconnu"] = out["type_bien"].map(lambda x: bool(x and known_types and x.casefold() not in known_types))
    geo_path = Path(root)/"data"/"raw"/"referentiels"/"referentiel_geographique.csv"
    if geo_path.exists():
        geo = pd.read_csv(geo_path, encoding="utf-8-sig")
        pairs = set(zip(geo["region"].astype(str).str.casefold(), geo["ville"].astype(str).str.casefold()))
    else: pairs = set()
    def _geo_incoherente(row):
        region, ville = row.get("region"), row.get("ville")
        # Les cellules vides deviennent souvent NaN (float) dans pandas.
        if pd.isna(region) or pd.isna(ville) or not pairs:
            return False  # les manquants sont comptabilisés séparément dans le rapport
        region, ville = str(region).strip().casefold(), str(ville).strip().casefold()
        if not region or not ville:
            return False
        return (region, ville) not in pairs
    out["geo_incoherente"] = out.apply(_geo_incoherente, axis=1)
    return out, stats


def _norm_key(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def detect_duplicates(df: pd.DataFrame):
    """Doublons exacts sur attributs métier et candidats probables non fusionnés."""
    out = df.copy()
    key_cols = ["date", "ville", "type_bien", "prix_fcfa", "surface_m2"]
    out["cle_doublon"] = out.apply(lambda r: "|".join("" if pd.isna(r[c]) else str(r[c]) for c in key_cols), axis=1)
    out["doublon_exact"] = out.duplicated(key_cols, keep="first") & out[key_cols].notna().all(axis=1)
    probable = [False] * len(out)
    records = out.to_dict("records")
    groups = {}
    for i, r in enumerate(records):
        if pd.isna(r["date"]) or pd.isna(r["surface_m2"]) or pd.isna(r["prix_fcfa"]) or not r["ville"] or not r["type_bien"]:
            continue
        key = (_norm_key(r["ville"]), _norm_key(r["type_bien"]))
        groups.setdefault(key, []).append((i, r))
    for members in groups.values():
        for pos, (i, a) in enumerate(members):
            for j, b in members[pos+1:]:
                if a["source"] == b["source"]:
                    continue
                surf_a, surf_b = float(a["surface_m2"]), float(b["surface_m2"])
                prix_a, prix_b = float(a["prix_fcfa"]), float(b["prix_fcfa"])
                surf_rel = abs(surf_a-surf_b) / max(surf_a, surf_b, 1)
                prix_rel = abs(prix_a-prix_b) / max(prix_a, prix_b, 1)
                days = abs((a["date"]-b["date"]).days)
                if surf_rel <= .02 and prix_rel <= .03 and days <= 30:
                    probable[i] = True
                    probable[j] = True
    out["doublon_probable"] = probable
    return out


def validate(df: pd.DataFrame, today=None):
    out = df.copy()
    today = pd.Timestamp(today or pd.Timestamp.today().normalize())
    reasons, warnings = [], []
    for _, r in out.iterrows():
        err, warn = [], []
        if pd.isna(r["id_source"]) or not str(r["id_source"]).strip(): err.append("identifiant_absent")
        if pd.isna(r["prix_fcfa"]) or r["prix_fcfa"] <= 0: err.append("prix_absent_ou_invalide")
        if pd.isna(r["surface_m2"]) or r["surface_m2"] <= 0: err.append("surface_absente_ou_invalide")
        if pd.isna(r["date"]): err.append("date_absente_ou_ininterpretable")
        if str(r.get("statut") if pd.notna(r.get("statut")) else "").strip().casefold() in {"vendu", "vendue", "vendu(e)", "loué", "loue", "loue(e)"} and pd.notna(r["date"]) and r["date"] > today:
            err.append("date_future_transaction_finalisee")
        if pd.notna(r["surface_m2"]) and (r["surface_m2"] < 5 or r["surface_m2"] > 2000): warn.append("surface_atypique")
        if pd.notna(r["prix_fcfa"]) and (r["prix_fcfa"] < 100_000 or r["prix_fcfa"] > 2_000_000_000): warn.append("prix_atypique")
        if bool(r.get("geo_incoherente", False)): warn.append("ville_region_incompatible_referentiel")
        if bool(r.get("type_inconnu", False)): warn.append("type_absent_referentiel")
        if bool(r.get("doublon_probable", False)): warn.append("doublon_probable_a_verifier")
        if bool(r.get("doublon_exact", False)): warn.append("doublon_exact_conserve_pour_audit")
        reasons.append(";".join(err))
        warnings.append(";".join(warn))
    out["motifs_quarantaine"] = reasons
    out["avertissements"] = warnings
    out["decision"] = ["quarantaine" if e else ("avertissement" if w else "conforme") for e,w in zip(reasons,warnings)]
    return out


def quality_report(df, stats, output_dir: Path):
    total = len(df)
    missing = df[CANONICAL].isna().sum().sort_values(ascending=False)
    by_source = df.groupby("source").agg(enregistrements=("id_source","size"), quarantaine=("decision",lambda s:(s=="quarantaine").sum()), 
                                         avertissements=("decision",lambda s:(s=="avertissement").sum()), conformes=("decision",lambda s:(s=="conforme").sum()))
    n_exact = int(df["doublon_exact"].sum())
    n_prob = int(df["doublon_probable"].sum())
    n_q = int((df["decision"]=="quarantaine").sum())
    n_warn = int((df["decision"]=="avertissement").sum())
    n_ok = int((df["decision"]=="conforme").sum())
    lines = ["# Rapport qualité — ImmoAnalyse", "", f"Généré le : {pd.Timestamp.now():%Y-%m-%d %H:%M}", "", 
             "## Synthèse", "", f"- Enregistrements analysés : **{total}**", f"- Conservés conformes : **{n_ok}** ({n_ok/total:.1%} du total si total non nul)" 
             if total else "- Conservés conformes : 0", f"- Conservés avec avertissement : **{n_warn}**", f"- Mis en quarantaine : **{n_q}**", 
             f"- Doublons exacts signalés : **{n_exact}**", f"- Enregistrements impliqués dans un doublon probable : **{n_prob}**", "", "## Résultats par source", 
             "", by_source.to_markdown(), "", "## Valeurs manquantes (schéma canonique)", "", missing.rename("valeurs_manquantes").to_frame().to_markdown(), "", 
             "## Échecs de conversion", "", pd.Series(stats["conversions_echouees"], name="échecs").to_frame().to_markdown(), "", "## Méthode et limites", "", 
             "- Les fichiers bruts ne sont jamais modifiés.", "- Les corrections de format (espaces, casse, dates et nombres) sont appliquées de façon déterministe.", 
             "- Les valeurs atypiques sont conservées avec avertissement ; elles ne sont pas supprimées automatiquement.", 
             "- Les villes/régions incompatibles avec le référentiel sont signalées sans correction automatique.", 
             "- Les doublons exacts sont signalés ; les doublons probables sont des candidats inter-sources selon ville, type, surface (±2 %), prix (±3 %) et date (±30 jours). Aucun rapprochement probabiliste n'est fusionné automatiquement.", 
             "- Le champ transaction peut être absent lorsque la source ne l'indique pas.", "- Les données sont synthétiques et ne représentent pas des transactions immobilières réelles.", ""]
    (output_dir/"rapport_qualite.md").write_text("\n".join(lines), encoding="utf-8")


def run_pipeline(root: Path):
    root = Path(root)
    outdir = root / "sortie"
    outdir.mkdir(parents=True, exist_ok=True)
    (root / "data" / "staging").mkdir(parents=True, exist_ok=True)
    (root / "data" / "processed").mkdir(parents=True, exist_ok=True)
    raw = load_sources(root)
    raw.to_csv(root / "data" / "staging" / "ingestion_canonique.csv", index=False, encoding="utf-8-sig")
    normalized, stats = normalize(raw, root)
    with_dupes = detect_duplicates(normalized)
    checked = validate(with_dupes)
    clean_cols = CANONICAL + ["doublon_exact", "doublon_probable", "avertissements", "decision"]
    quarantine_cols = CANONICAL + ["motifs_quarantaine", "avertissements", "doublon_exact", "doublon_probable"]
    clean = checked.loc[checked["decision"] != "quarantaine", clean_cols].copy()
    quarantine = checked.loc[checked["decision"] == "quarantaine", quarantine_cols].copy()
    clean.to_csv(outdir/"donnees_propres.csv", index=False, encoding="utf-8-sig")
    clean.to_json(outdir/"donnees_propres.json", orient="records", force_ascii=False, date_format="iso", indent=2)
    quarantine.to_csv(outdir/"quarantaine.csv", index=False, encoding="utf-8-sig")
    checked.to_csv(outdir/"audit_complet.csv", index=False, encoding="utf-8-sig")
    clean.to_csv(root / "data" / "processed" / "donnees_propres.csv", index=False, encoding="utf-8-sig")
    quarantine.to_csv(root / "data" / "processed" / "quarantaine.csv", index=False, encoding="utf-8-sig")
    quality_report(checked, stats, outdir)
    # Profilage reproductible par source
    profile = checked.groupby("source").agg(lignes=("id_source","size"), identifiants_manquants=("id_source",lambda s:s.isna().sum()), 
                                            dates_manquantes=("date",lambda s:s.isna().sum()), prix_manquants=("prix_fcfa",lambda s:s.isna().sum()), 
                                            surfaces_manquantes=("surface_m2",lambda s:s.isna().sum()), doublons_exacts=("doublon_exact","sum"), 
                                            doublons_probables=("doublon_probable","sum"))
    profile.to_csv(outdir/"profil_sources.csv", encoding="utf-8-sig")
    return checked
