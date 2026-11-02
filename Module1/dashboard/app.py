"""Tableau de bord décisionnel IMMO_ANALYSE (Dash).
Lancement depuis la racine du projet : python dashboard/app.py
Les fichiers sources et sorties sont lus uniquement, jamais modifiés.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Input, Output
from flask import send_file, abort

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "avant": ROOT / "data/staging/ingestion_canonique.csv",
    "propre": ROOT / "data/processed/donnees_propres.csv",
    "quarantaine": ROOT / "data/processed/quarantaine.csv",
    "audit": ROOT / "sortie/audit_complet.csv",
}

def lire_csv(path):
    """Lecture robuste ; un fichier absent produit un tableau vide, pas des données fictives."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", low_memory=False)

def preparer(df):
    """Convertit les champs analytiques sans écrire dans les fichiers."""
    df = df.copy()
    for col in ["prix_fcfa", "surface_m2", "pieces", "sdb"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "date" in df:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["source", "transaction", "type_bien", "region", "ville", "statut"]:
        if col in df:
            df[col] = df[col].fillna("Non renseigné").astype(str).str.strip()
    return df

AVANT = preparer(lire_csv(PATHS["avant"]))
PROPRE = preparer(lire_csv(PATHS["propre"]))
QUARANTAINE = preparer(lire_csv(PATHS["quarantaine"]))
AUDIT = preparer(lire_csv(PATHS["audit"]))
DISPONIBLE = not AVANT.empty and not PROPRE.empty

def pourcentage(n, d):
    """Retourne un taux avec dénominateur nul protégé."""
    return 100 * n / d if d else 0.0

def filtrer(df, regions, categories, transactions, sources):
    """Applique les mêmes filtres à chaque ensemble comparable."""
    df = df.copy()
    for col, values in [("region", regions), ("type_bien", categories),
                        ("transaction", transactions), ("source", sources)]:
        if values and col in df:
            df = df[df[col].isin(values)]
    return df

def kpi(titre, valeur, note, classe="blue"):
    return html.Div([html.Div(titre, className="kpi-title"),
                     html.Div(valeur, className="kpi-value"),
                     html.Div(note, className="kpi-note")], className=f"kpi {classe}")

def format_fcfa(v):
    return "—" if pd.isna(v) else f"{v:,.0f}".replace(",", " ") + " FCFA"

def mise_en_forme(fig, hauteur=340):
    fig.update_layout(template="plotly_white", height=hauteur,
                      margin=dict(l=25, r=20, t=55, b=35),
                      font=dict(family="Arial, sans-serif", color="#263449", size=12),
                      title_font=dict(size=16, color="#172b4d"), paper_bgcolor="white",
                      plot_bgcolor="white", legend_title_text="")
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#e9eef5", zeroline=False, automargin=True)
    return fig

def figure_vide(texte="Aucune donnée disponible pour ces filtres"):
    f = go.Figure()
    f.add_annotation(text=texte, x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
    return mise_en_forme(f)

REGIONS = sorted(PROPRE["region"].dropna().unique()) if "region" in PROPRE else []
CATEGORIES = sorted(PROPRE["type_bien"].dropna().unique()) if "type_bien" in PROPRE else []
SOURCES = sorted(PROPRE["source"].dropna().unique()) if "source" in PROPRE else []
TRANSACTIONS = sorted(PROPRE["transaction"].dropna().unique()) if "transaction" in PROPRE else []

app = Dash(__name__, title="IMMO_ANALYSE | Dashboard", suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([
    html.Header([html.Div([html.Div("IA", className="logo"), html.Div([
        html.Div("IMMO_ANALYSE", className="brand-title"),
        html.Div("Pilotage de la qualité des données immobilières", className="brand-subtitle")
    ])], className="brand"), html.Div("TABLEAU DE BORD • SÉNÉGAL", className="badge")], className="header"),
    html.Div([
        html.Div([html.Label("Région"), dcc.Dropdown(id="f-region", options=[{"label":x,"value":x} for x in REGIONS], multi=True, placeholder="Toutes les régions")], className="filter"),
        html.Div([html.Label("Catégorie"), dcc.Dropdown(id="f-categorie", options=[{"label":x.title(),"value":x} for x in CATEGORIES], multi=True, placeholder="Toutes les catégories")], className="filter"),
        html.Div([html.Label("Transaction"), dcc.Dropdown(id="f-transaction", options=[{"label":x.title(),"value":x} for x in TRANSACTIONS], multi=True, placeholder="Toutes les transactions")], className="filter"),
        html.Div([html.Label("Source"), dcc.Dropdown(id="f-source", options=[{"label":x.replace('_',' ').title(),"value":x} for x in SOURCES], multi=True, placeholder="Toutes les sources")], className="filter"),
        html.Button("Réinitialiser", id="reset", n_clicks=0, className="reset")
    ], className="filters"),
    dcc.Tabs(id="menu", value="general", className="menu", children=[
        dcc.Tab(label="Vue générale", value="general", className="tab", selected_className="tab-selected"),
        dcc.Tab(label="Qualité avant / après", value="qualite", className="tab", selected_className="tab-selected"),
        dcc.Tab(label="Analyse immobilière", value="marche", className="tab", selected_className="tab-selected"),
        dcc.Tab(label="Sources & traçabilité", value="sources", className="tab", selected_className="tab-selected"),
        dcc.Tab(label="Quarantaine", value="quarantaine", className="tab", selected_className="tab-selected"),
    ]),
    html.Main(id="contenu", className="content"),
    html.Footer([html.Span("IMMO_ANALYSE · Dashboard analytique"), html.Span("Données synthétiques — ne pas interpréter comme des prix réels du marché.")], className="footer")
], className="app")

@app.callback(Output("f-region","value"), Output("f-categorie","value"), Output("f-transaction","value"), Output("f-source","value"), Input("reset","n_clicks"), prevent_initial_call=True)
def reinitialiser(_):
    return [], [], [], []

@app.callback(Output("contenu","children"), Input("menu","value"), Input("f-region","value"), Input("f-categorie","value"), Input("f-transaction","value"), Input("f-source","value"))
def afficher(page, regions, categories, transactions, sources):
    if not DISPONIBLE:
        return html.Div([html.H2("Données du projet introuvables"), html.P("Vérifiez data/staging/ingestion_canonique.csv et data/processed/donnees_propres.csv.")], className="panel")
    regions, categories, transactions, sources = [x or [] for x in (regions,categories,transactions,sources)]
    avant = filtrer(AVANT, regions,categories,transactions,sources)
    propre = filtrer(PROPRE, regions,categories,transactions,sources)
    quar = filtrer(QUARANTAINE, regions,categories,transactions,sources)
    nb_avant, nb_propre, nb_quar = len(avant), len(propre), len(quar)
    total = nb_propre + nb_quar
    retention = pourcentage(nb_propre,total)
    prix_manquant_avant = int(avant["prix_fcfa"].isna().sum()) if "prix_fcfa" in avant else 0
    prix_manquant_apres = int(propre["prix_fcfa"].isna().sum()) if "prix_fcfa" in propre else 0
    surf_manquant_avant = int(avant["surface_m2"].isna().sum()) if "surface_m2" in avant else 0
    surf_manquant_apres = int(propre["surface_m2"].isna().sum()) if "surface_m2" in propre else 0
    avert = int(propre["avertissements"].fillna("").astype(str).str.strip().ne("").sum()) if "avertissements" in propre else 0
    prix_valides = propre.loc[propre["prix_fcfa"].gt(0),"prix_fcfa"] if "prix_fcfa" in propre else pd.Series(dtype=float)
    surf_valides = propre.loc[propre["surface_m2"].gt(0),"surface_m2"] if "surface_m2" in propre else pd.Series(dtype=float)
    mediane_prix = prix_valides.median() if len(prix_valides) else np.nan
    mediane_surface = surf_valides.median() if len(surf_valides) else np.nan
    p2 = propre.loc[propre["prix_fcfa"].gt(0) & propre["surface_m2"].gt(0)].copy() if {"prix_fcfa","surface_m2"}.issubset(propre.columns) else pd.DataFrame()
    if not p2.empty: p2["prix_m2"] = p2["prix_fcfa"] / p2["surface_m2"]

    # Graphique de comparaison : nombre de champs prix/surface manquants.
    qc = pd.DataFrame({"Champ":["Prix manquant","Surface manquante"],
        "Avant nettoyage":[prix_manquant_avant,surf_manquant_avant],
        "Après nettoyage":[prix_manquant_apres,surf_manquant_apres]})
    fig_q = px.bar(qc, x="Champ", y=["Avant nettoyage","Après nettoyage"], barmode="group", title="Champs manquants — comparaison avant / après", labels={"value":"Nombre de lignes","variable":"Étape"})
    mise_en_forme(fig_q)
    fig_dec = px.pie(pd.DataFrame({"Décision":["Admis après contrôles","Quarantaine"],"Lignes":[nb_propre,nb_quar]}), names="Décision", values="Lignes", hole=.6, title="Devenir des enregistrements")
    fig_dec.update_traces(textinfo="label+percent", textposition="inside"); mise_en_forme(fig_dec)
    if not propre.empty and "source" in propre:
        ds = propre.groupby("source").size().reset_index(name="Annonces").sort_values("Annonces")
        fig_source = px.bar(ds,x="Annonces",y="source",orientation="h",text="Annonces",title="Annonces admises par source"); fig_source.update_traces(textposition="outside"); mise_en_forme(fig_source)
    else: fig_source = figure_vide()
    if not propre.empty and {"type_bien","prix_fcfa"}.issubset(propre.columns):
        dc = propre[propre["prix_fcfa"].gt(0)].groupby("type_bien")["prix_fcfa"].median().div(1_000_000).reset_index(name="Prix médian (millions FCFA)").sort_values("Prix médian (millions FCFA)",ascending=False)
        fig_cat = px.bar(dc,x="type_bien",y="Prix médian (millions FCFA)",title="Prix médian par catégorie",text_auto=".1f"); mise_en_forme(fig_cat)
    else: fig_cat = figure_vide()
    if not propre.empty and "region" in propre:
        dr = propre.groupby("region").size().reset_index(name="Annonces").nlargest(12,"Annonces").sort_values("Annonces")
        fig_region = px.bar(dr,x="Annonces",y="region",orientation="h",title="12 régions les plus représentées"); mise_en_forme(fig_region,380)
    else: fig_region = figure_vide()
    if not p2.empty:
        # Filtre visuel P99 seulement : les valeurs du fichier ne sont pas altérées.
        vis = p2[p2["prix_m2"] <= p2["prix_m2"].quantile(.99)]
        fig_scatter = px.scatter(vis,x="surface_m2",y="prix_m2",color="type_bien" if "type_bien" in vis else None,hover_data=[x for x in ["region","ville","transaction","prix_fcfa"] if x in vis],title="Surface et prix au m² (échelle visuelle jusqu'au P99)",labels={"surface_m2":"Surface (m²)","prix_m2":"Prix au m² (FCFA)"}); mise_en_forme(fig_scatter,390)
    else: fig_scatter = figure_vide("Prix et surface positifs insuffisants pour calculer le prix au m²")

    def graph(fig): return html.Div(dcc.Graph(figure=fig,config={"displayModeBar":False},responsive=True),className="panel chart")
    def grid(items): return html.Div(items,className="kpis")
    def heading(t,s): return html.Div([html.Div([html.H1(t),html.P(s)]),html.Div(f"{total:,} lignes traitées".replace(","," "),className="pill")],className="heading")

    if page == "general":
        return html.Div([heading("Vue générale","Volumes, fiabilité et structure du portefeuille de données."),
            grid([kpi("Avant nettoyage",f"{nb_avant:,}".replace(","," "),"Données canoniques harmonisées","blue"),kpi("Admis après contrôles",f"{nb_propre:,}".replace(","," "),f"Rétention : {retention:.1f} % du total traité","green"),kpi("Quarantaine",f"{nb_quar:,}".replace(","," "),f"{pourcentage(nb_quar,total):.1f} % du total traité","orange"),kpi("Avec avertissements",f"{avert:,}".replace(","," "),"Parmi les lignes admises filtrées","purple")]),
            html.Div([graph(fig_dec),graph(fig_q)],className="columns"),html.Div([graph(fig_source),graph(fig_region)],className="columns"),
            html.Div([html.H3("À retenir pour décider"),html.Ul([html.Li("Suivre la quarantaine : elle représente le volume à revoir avant exploitation."),html.Li("Prioriser les sources qui pèsent le plus dans le volume, puis comparer leur complétude."),html.Li("La médiane limite l'influence des prix extrêmes."),html.Li("Les données sont synthétiques et ne donnent pas une estimation du marché réel.")])],className="insight")])
    if page == "qualite":
        return html.Div([heading("Qualité avant / après","Mesures de complétude et devenir des lignes ; chaque taux affiche son dénominateur."),
            grid([kpi("Prix manquants avant",f"{prix_manquant_avant:,}".replace(","," "),f"{pourcentage(prix_manquant_avant,nb_avant):.1f} % des {nb_avant:,} lignes d'entrée","orange"),kpi("Prix manquants après",f"{prix_manquant_apres:,}".replace(","," "),f"{pourcentage(prix_manquant_apres,nb_propre):.1f} % des {nb_propre:,} lignes admises","green"),kpi("Doublons exacts",str(int(propre.get("doublon_exact",pd.Series(dtype=bool)).fillna(False).astype(str).str.lower().isin(["true","1","oui"]).sum())),"Signalés dans les lignes admises","blue"),kpi("Doublons probables",str(int(propre.get("doublon_probable",pd.Series(dtype=bool)).fillna(False).astype(str).str.lower().isin(["true","1","oui"]).sum())),"À vérifier, pas à supprimer sans revue","purple")]),
            html.Div([graph(fig_q),graph(fig_dec)],className="columns"),graph(fig_cat),html.Div([html.H3("Définition du périmètre"),html.P("L'« avant » correspond aux données canoniques après harmonisation à l'ingestion, et non aux fichiers bruts hétérogènes. L'« après » correspond aux lignes admises ; la quarantaine est isolée. Un champ non évaluable ne doit pas être compté comme conforme.")],className="insight")])
    if page == "marche":
        return html.Div([heading("Analyse immobilière","Indicateurs descriptifs filtrables pour comprendre la composition des annonces."),
            grid([kpi("Prix médian",format_fcfa(mediane_prix),"Prix strictement positifs","blue"),kpi("Surface médiane",f"{mediane_surface:,.1f} m²".replace(","," ") if pd.notna(mediane_surface) else "—","Surfaces strictement positives","green"),kpi("Prix médian au m²",format_fcfa(p2["prix_m2"].median()) if not p2.empty else "—","Prix et surface positifs","purple"),kpi("Annonces admises",f"{nb_propre:,}".replace(","," "),"Selon les filtres sélectionnés","orange")]),
            html.Div([graph(fig_cat),graph(fig_region)],className="columns"),graph(fig_scatter),html.Div([html.H3("Précautions"),html.P("Comparez séparément ventes et locations. Le prix au m² est prix / surface. Les valeurs au-dessus du 99e percentile sont masquées uniquement dans le nuage pour préserver la lisibilité ; aucune ligne n'est supprimée du fichier source.")],className="insight")])
    if page == "sources":
        if not propre.empty:
            stats = propre.groupby("source").agg(lignes=("source","size"),prix_manquants=("prix_fcfa",lambda x:int(x.isna().sum())),surfaces_manquantes=("surface_m2",lambda x:int(x.isna().sum()))).reset_index()
        else: stats = pd.DataFrame(columns=["source","lignes","prix_manquants","surfaces_manquantes"])
        tab = dash_table.DataTable(data=stats.to_dict("records"),columns=[{"name":x.replace("_"," ").title(),"id":x} for x in stats.columns],page_size=10,sort_action="native",style_table={"overflowX":"auto"},style_header={"backgroundColor":"#edf2f7","fontWeight":"bold"},style_cell={"padding":"10px","fontSize":"13px","textAlign":"left"})
        return html.Div([heading("Sources & traçabilité","Comparer la contribution et les champs manquants de chaque source."),grid([kpi("Sources représentées",str(propre["source"].nunique() if "source" in propre else 0),"Dans les lignes admises","blue"),kpi("Lignes admises",f"{nb_propre:,}".replace(","," "),"Sous-ensemble filtré","green"),kpi("Prix manquants",str(prix_manquant_apres),"Lignes admises","orange"),kpi("Surfaces manquantes",str(surf_manquant_apres),"Lignes admises","purple")]),graph(fig_source),html.Div([html.H3("Profil des sources"),tab],className="panel"),html.Div([html.H3("Traçabilité"),html.P("Les identifiants source sont conservés pour faciliter le retour à l'enregistrement d'origine. L'aperçu agrégé ci-dessus est calculé à partir des lignes admises.")],className="insight"),html.A("Télécharger les données propres (CSV)",href="/exports/donnees_propres.csv",className="download")])
    # La page quarantaine permet le tri, le filtrage et la revue des motifs.
    motifs = quar["motifs_quarantaine"].fillna("Motif non renseigné").astype(str).str.split(";").explode().str.strip() if "motifs_quarantaine" in quar else pd.Series(dtype=str)
    dm = motifs.value_counts().head(12).sort_values().reset_index() if not motifs.empty else pd.DataFrame()
    if not dm.empty:
        dm.columns=["Motif","Occurrences"]; fig_motif=px.bar(dm,x="Occurrences",y="Motif",orientation="h",title="Principaux motifs de quarantaine");mise_en_forme(fig_motif,400)
    else: fig_motif=figure_vide("Aucun motif disponible")
    cols=[x for x in ["id_source","source","date","transaction","type_bien","region","ville","prix_fcfa","surface_m2","motifs_quarantaine","avertissements"] if x in quar]
    qview=quar[cols].head(500)
    qt=dash_table.DataTable(data=qview.to_dict("records"),columns=[{"name":x.replace("_"," ").title(),"id":x} for x in cols],page_size=12,sort_action="native",filter_action="native",style_table={"overflowX":"auto"},style_header={"backgroundColor":"#fff1f2","fontWeight":"bold"},style_cell={"padding":"9px","fontSize":"12px","textAlign":"left","minWidth":"90px","maxWidth":"250px","whiteSpace":"normal"})
    return html.Div([heading("Quarantaine","Ces enregistrements nécessitent une revue avant utilisation analytique."),grid([kpi("Lignes en quarantaine",f"{nb_quar:,}".replace(","," "),f"{pourcentage(nb_quar,total):.1f} % du total traité","orange"),kpi("Motifs distincts",str(motifs.nunique() if not motifs.empty else 0),"Motifs disponibles","purple"),kpi("Lignes visibles",str(len(qview)),"Aperçu plafonné à 500 lignes","blue"),kpi("Action", "Revue manuelle","Ne pas deviner les valeurs ambiguës","green")]),graph(fig_motif),html.Div([html.H3("Détail de la quarantaine"),qt],className="panel"),html.P("L'aperçu est limité à 500 lignes ; le fichier quarantaine.csv contient l'ensemble des lignes.",className="note")])

@server.route("/exports/donnees_propres.csv")
def telecharger_propre():
    if not PATHS["propre"].exists(): abort(404)
    return send_file(PATHS["propre"],as_attachment=True,download_name="donnees_propres.csv")

if __name__ == "__main__":
    app.run(debug=False,host="127.0.0.1",port=8050)
