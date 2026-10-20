"""
Acteurs français dans les projets européens de recherche (Horizon 2020 + Horizon Europe)
Application Streamlit qui lit l'export Excel produit par le notebook Colab CORDIS.
"""
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Acteurs français · projets européens", page_icon="🇪🇺", layout="wide")

DOSSIER_DATA = Path(__file__).parent / "data"
BLEU, ORANGE, VERT, VIOLET, GRIS = "#4C78A8", "#F58518", "#54A24B", "#B279A2", "#9D9D9D"
COUL_PAYS = {"FR": BLEU, "DE": ORANGE}
COUL_PROG = {"Horizon 2020": "#72B7B2", "Horizon Europe": "#E45756"}
DOM_AUTO = ["Routier & automobile", "Véhicule connecté et autonome (CCAM)", "Batteries (tous usages)"]


# ---------------------------------------------------------------- utilitaires
def fr(x, dec=0):
    """Nombre au format français : 1 234,5"""
    if x is None or pd.isna(x):
        return "—"
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


@st.cache_data(show_spinner="Lecture du fichier…")
def lire_excel(contenu: bytes) -> dict:
    return pd.read_excel(BytesIO(contenu), sheet_name=None)


def fichier_par_defaut():
    fichiers = sorted(DOSSIER_DATA.glob("*.xlsx"))
    return fichiers[-1] if fichiers else None


def telecharger_excel(df: pd.DataFrame, nom: str, label="Télécharger (Excel)"):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    st.download_button(label, buf.getvalue(), file_name=nom,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def mise_en_forme(fig, hauteur=None):
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), legend_title_text="",
                      font=dict(size=13), separators=", ", hovermode="closest")
    if hauteur:
        fig.update_layout(height=hauteur)
    return fig


# ---------------------------------------------------------------- données
with st.sidebar:
    st.header("Données")
    depot = st.file_uploader("Charger un autre export Excel du notebook", type="xlsx",
                             help="Par défaut, l'application lit le fichier le plus récent du dossier data/ du dépôt.")
    defaut = fichier_par_defaut()
    if depot is not None:
        X = lire_excel(depot.getvalue())
        st.caption(f"Fichier chargé : {depot.name}")
    elif defaut is not None:
        X = lire_excel(defaut.read_bytes())
        st.caption(f"Fichier du dépôt : {defaut.name}")
    else:
        st.warning("Aucun fichier dans data/. Chargez l'export Excel du notebook.")
        st.stop()

ONGLETS_REQUIS = ["Synthese", "Domaines_France", "FR_DE_auto", "FR_DE_auto_annee", "Top_auto_FR", "Top_auto_DE",
                  "Par_annee", "Transport_par_annee", "Comparaison_pays", "Regions", "Liste_acteurs_FR"]
manquants = [o for o in ONGLETS_REQUIS if o not in X]
if manquants:
    st.error(f"Ce fichier ne contient pas les onglets attendus : {', '.join(manquants)}. "
             "Utilisez l'export de la version « acteurs » du notebook.")
    st.stop()

synth = X["Synthese"].copy()
synth["Programme"] = synth["Programme"].str.replace(r"Total.*", "Total 2014-2026", regex=True)
synth["Catégorie"] = synth["Catégorie"].str.replace(r"Laboratoires.*", "Laboratoires", regex=True)
dom = X["Domaines_France"]
frde = X["FR_DE_auto"]
frde_an = X["FR_DE_auto_annee"]
top = pd.concat([X["Top_auto_FR"].assign(pays="FR"), X["Top_auto_DE"].assign(pays="DE")], ignore_index=True)
par_an = pd.concat([X["Par_annee"].assign(perimetre="Tous domaines"),
                    X["Transport_par_annee"].assign(perimetre="Transports")], ignore_index=True)
pays = X["Comparaison_pays"]
reg = X["Regions"]
acteurs = X["Liste_acteurs_FR"]
COLS_DOM = {c: c.replace("projets · ", "") for c in acteurs.columns if c.startswith("projets · ")}


def val(df, filtre: dict, col):
    d = df
    for k, v in filtre.items():
        d = d[d[k] == v]
    return d[col].iloc[0] if len(d) else None


# ---------------------------------------------------------------- en-tête
st.title("Acteurs français dans les projets européens")
tot_e = {"Périmètre": "Tous domaines", "Programme": "Total 2014-2026", "Catégorie": "Entreprises"}
tot_auto = {"Domaine": "Total secteur auto", "Catégorie": "Tous acteurs"}
st.markdown(
    f"Depuis 2014, **{fr(val(synth, tot_e, 'Acteurs distincts (PIC)'))}** entreprises françaises ont participé à "
    f"Horizon 2020 et Horizon Europe, pour **{fr(val(synth, tot_e, 'Contribution UE (M€)'), 1)} M€** de contribution UE. "
    f"Sur le secteur automobile, les acteurs français reçoivent **{fr(val(frde, tot_auto, 'Contribution UE (M€) FR'), 1)} M€** "
    f"contre **{fr(val(frde, tot_auto, 'Contribution UE (M€) DE'), 1)} M€** pour les acteurs allemands "
    f"(ratio **{fr(val(frde, tot_auto, 'Ratio contribution FR/DE'), 2)}**).")

t1, t2, t3, t4, t5, t6 = st.tabs(["Vue d'ensemble", "Domaines", "France – Allemagne : automobile",
                                  "Acteurs", "Régions", "Méthode et contrôle"])

# ================================================================ Vue d'ensemble
with t1:
    c1, c2 = st.columns(2)
    perim = c1.segmented_control("Périmètre", ["Tous domaines", "Transports"], default="Tous domaines", key="perim") or "Tous domaines"
    prog = c2.segmented_control("Programme", ["Total 2014-2026", "Horizon 2020", "Horizon Europe"],
                                default="Total 2014-2026", key="prog") or "Total 2014-2026"
    fe = {"Périmètre": perim, "Programme": prog, "Catégorie": "Entreprises"}
    fl = {"Périmètre": perim, "Programme": prog, "Catégorie": "Laboratoires"}
    k = st.columns(5)
    k[0].metric("Entreprises distinctes", fr(val(synth, fe, "Acteurs distincts (PIC)")),
                help=f"dont PME : {fr(val(synth, fe, 'dont PME'))}")
    k[1].metric("Contribution UE aux entreprises", f"{fr(val(synth, fe, 'Contribution UE (M€)'), 1)} M€",
                help=f"{fr(val(synth, fe, 'Participations'))} participations")
    k[2].metric("Laboratoires distincts", fr(val(synth, fl, "Acteurs distincts (PIC)")),
                help="Organismes de recherche et universités")
    k[3].metric("Contribution UE aux laboratoires", f"{fr(val(synth, fl, 'Contribution UE (M€)'), 1)} M€")
    k[4].metric("Coordinations par des entreprises", fr(val(synth, fe, "Coordinations")),
                help=f"sur {fr(val(synth, fe, 'Projets'))} projets")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Entreprises françaises par année")
        mes = st.radio("Mesure", ["Entreprises distinctes", "Nouvelles entreprises", "Contribution UE (M€)"],
                       horizontal=True, key="mes_an")
        d = par_an[par_an["perimetre"] == perim]
        if prog != "Total 2014-2026":
            d = d[d["programme"] == prog]
        if mes == "Nouvelles entreprises":
            d2 = d.groupby("annee", as_index=False)["nouvelles_entreprises"].max()
            fig = px.bar(d2, x="annee", y="nouvelles_entreprises", color_discrete_sequence=[BLEU],
                         labels={"annee": "Année de signature", "nouvelles_entreprises": "Nouvelles entreprises"})
        else:
            col = "entreprises" if mes == "Entreprises distinctes" else "contribution_UE_Meur"
            fig = px.bar(d, x="annee", y=col, color="programme", color_discrete_map=COUL_PROG,
                         labels={"annee": "Année de signature", col: mes, "programme": ""})
        st.plotly_chart(mise_en_forme(fig, 380), width="stretch")
        st.caption("Par année de signature. 2025 et 2026 sont incomplètes ; les projets Horizon 2020 de 2021 sont des signatures tardives.")
    with g2:
        st.subheader("Entreprises : la France face aux autres pays")
        opts = {"Entreprises distinctes": "entreprises", "Contribution UE (M€)": "contribution_UE_Meur",
                "Entreprises distinctes – transports": "entreprises_transport",
                "Contribution UE transports (M€)": "contribution_transport_Meur",
                "Part de la contribution UE aux entreprises (%)": "part_contribution_entreprises_%"}
        lab = st.selectbox("Mesure", list(opts), key="mes_pays")
        d = pays.sort_values(opts[lab])
        fig = px.bar(d, x=opts[lab], y="pays", orientation="h", text_auto=True,
                     color=d["pays"].eq("FR").map({True: "France", False: "Autres pays"}),
                     color_discrete_map={"France": BLEU, "Autres pays": GRIS}, labels={opts[lab]: lab, "pays": ""})
        fig.update_layout(showlegend=False)
        st.plotly_chart(mise_en_forme(fig, 380), width="stretch")
        st.caption("Entreprises uniquement (type PRC), 2014-2026.")

# ================================================================ Domaines
with t2:
    st.subheader("Position de la France par domaine")
    mes = st.radio("Mesure", ["Part UE (%) : France et Allemagne", "Contribution France (M€)", "Acteurs français"],
                   horizontal=True, key="mes_dom")
    d = dom[dom["Domaine"] != "Autre transport"].copy()
    if mes.startswith("Part"):
        d = d.sort_values("Part FR (%)")
        long = d.melt(id_vars="Domaine", value_vars=["Part FR (%)", f"Part DE (%)"], var_name="Pays", value_name="Part (%)")
        long["Pays"] = long["Pays"].map({"Part FR (%)": "France", "Part DE (%)": "Allemagne"})
        fig = px.bar(long, x="Part (%)", y="Domaine", color="Pays", barmode="group", orientation="h", text_auto=".1f",
                     color_discrete_map={"France": BLEU, "Allemagne": ORANGE}, labels={"Domaine": ""})
    elif mes.startswith("Contribution"):
        d["autres acteurs"] = d["Contribution FR (M€)"] - d["dont entreprises (M€)"]
        d = d.sort_values("Contribution FR (M€)")
        long = d.melt(id_vars="Domaine", value_vars=["dont entreprises (M€)", "autres acteurs"], var_name="Type", value_name="M€")
        long["Type"] = long["Type"].replace({"dont entreprises (M€)": "Entreprises", "autres acteurs": "Autres acteurs"})
        fig = px.bar(long, x="M€", y="Domaine", color="Type", orientation="h",
                     color_discrete_map={"Entreprises": BLEU, "Autres acteurs": VERT}, labels={"Domaine": ""})
    else:
        d = d.sort_values("Entreprises FR")
        long = d.melt(id_vars="Domaine", value_vars=["Entreprises FR", "Laboratoires FR"], var_name="Type", value_name="Acteurs")
        fig = px.bar(long, x="Acteurs", y="Domaine", color="Type", orientation="h",
                     color_discrete_map={"Entreprises FR": BLEU, "Laboratoires FR": VERT}, labels={"Domaine": ""})
    st.plotly_chart(mise_en_forme(fig, 420), width="stretch")
    st.caption("Part de la contribution UE du domaine reçue par l'ensemble des acteurs du pays. Routier, CCAM et batteries "
               "incluent les projets repérés hors périmètre transports.")
    st.dataframe(dom, hide_index=True, width="stretch",
                 column_config={"Contribution FR (M€)": st.column_config.NumberColumn(format="%.1f"),
                                "dont entreprises (M€)": st.column_config.NumberColumn(format="%.1f")})

# ================================================================ France – Allemagne automobile
with t3:
    k = st.columns(5)
    k[0].metric("Contribution UE – France", f"{fr(val(frde, tot_auto, 'Contribution UE (M€) FR'), 1)} M€",
                help=f"{fr(val(frde, tot_auto, 'Part UE du domaine (%) FR'), 1)} % du secteur")
    k[1].metric("Contribution UE – Allemagne", f"{fr(val(frde, tot_auto, 'Contribution UE (M€) DE'), 1)} M€",
                help=f"{fr(val(frde, tot_auto, 'Part UE du domaine (%) DE'), 1)} % du secteur")
    k[2].metric("Ratio France / Allemagne", fr(val(frde, tot_auto, "Ratio contribution FR/DE"), 2))
    k[3].metric("Acteurs distincts FR / DE", f"{fr(val(frde, tot_auto, 'Acteurs distincts FR'))} / {fr(val(frde, tot_auto, 'Acteurs distincts DE'))}")
    k[4].metric("Coordinations FR / DE", f"{fr(val(frde, tot_auto, 'Coordinations FR'))} / {fr(val(frde, tot_auto, 'Coordinations DE'))}")
    st.caption("Secteur automobile = routier & automobile + véhicule connecté et autonome (CCAM) + batteries (tous usages).")

    c1, c2 = st.columns([2, 1])
    cat = c1.segmented_control("Catégorie d'acteurs", ["Tous acteurs", "Entreprises", "Organismes de recherche", "Universités et écoles"],
                               default="Tous acteurs", key="cat_auto") or "Tous acteurs"
    mesures = {"Contribution UE (M€)": "Contribution UE (M€)", "Acteurs distincts": "Acteurs distincts",
               "Coordinations": "Coordinations", "Part UE du domaine (%)": "Part UE du domaine (%)"}
    m = c2.selectbox("Mesure", list(mesures), key="mes_auto")
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("France et Allemagne par domaine")
        d = frde[(frde["Catégorie"] == cat) & frde["Domaine"].isin(DOM_AUTO)]
        long = d.melt(id_vars="Domaine", value_vars=[f"{m} FR", f"{m} DE"], var_name="Pays", value_name=m)
        long["Pays"] = long["Pays"].str[-2:].map({"FR": "France", "DE": "Allemagne"})
        fig = px.bar(long, x=m, y="Domaine", color="Pays", barmode="group", orientation="h", text_auto=True,
                     color_discrete_map={"France": BLEU, "Allemagne": ORANGE}, labels={"Domaine": ""})
        st.plotly_chart(mise_en_forme(fig, 380), width="stretch")
    with g2:
        st.subheader("Évolution annuelle : routier, automobile et CCAM")
        my = st.radio("Mesure", ["Contribution UE (M€)", "Acteurs", "Entreprises"], horizontal=True, key="mes_auto_an")
        pref = {"Contribution UE (M€)": "contribution_UE_Meur", "Acteurs": "acteurs", "Entreprises": "entreprises"}[my]
        fig = go.Figure()
        for p, nom in [("FR", "France"), ("DE", "Allemagne")]:
            colname = f"{pref} {p}"
            if colname in frde_an:
                fig.add_trace(go.Scatter(x=frde_an["annee"], y=frde_an[colname], mode="lines+markers", name=nom,
                                         line=dict(color=COUL_PAYS[p], width=2)))
        fig.update_layout(xaxis_title="Année de signature", yaxis_title=my, hovermode="x unified")
        st.plotly_chart(mise_en_forme(fig, 380), width="stretch")
        st.caption("2021 est l'année de transition entre programmes ; 2025 et 2026 sont incomplètes.")

    st.subheader("Principaux acteurs (routier, automobile et CCAM, filiales regroupées)")
    vmax = float(top["contribution_UE_Meur"].max())
    cfg = {"contribution_UE_Meur": st.column_config.ProgressColumn("Contribution (M€)", format="%.2f", min_value=0, max_value=vmax),
           "groupe": "Acteur", "categorie": "Catégorie", "projets": "Projets", "coordinations": "Coord.", "projets_CCAM": "dont CCAM"}
    a, b = st.columns(2)
    for colonne, p, titre in [(a, "FR", "France"), (b, "DE", "Allemagne")]:
        with colonne:
            st.markdown(f"**{titre}**")
            st.dataframe(top[top["pays"] == p].drop(columns="pays"), hide_index=True, width="stretch", column_config=cfg)
    with st.expander("Tableau détaillé France – Allemagne"):
        st.dataframe(frde, hide_index=True, width="stretch")

# ================================================================ Acteurs
with t4:
    st.subheader("Les acteurs français")
    st.caption("Tous les participants français (dédoublonnés par identifiant PIC). La contribution UE est le total de l'acteur, "
               "tous domaines confondus.")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    q = c1.text_input("Rechercher (nom, groupe, ville)", key="q_act")
    cats = c2.multiselect("Catégorie", sorted(acteurs["categorie"].dropna().unique()), key="cat_act")
    domaine = c3.selectbox("Domaine", ["Tous domaines"] + list(COLS_DOM.values()), key="dom_act")
    pme = c4.checkbox("PME seulement", key="pme_act")
    d = acteurs
    if q:
        txt = (d["nom"].fillna("") + " " + d["groupe"].fillna("") + " " + d["ville"].fillna("")).str.lower()
        d = d[txt.str.contains(q.lower(), regex=False)]
    if cats:
        d = d[d["categorie"].isin(cats)]
    col_dom = None
    if domaine != "Tous domaines":
        col_dom = next(c for c, v in COLS_DOM.items() if v == domaine)
        d = d[d[col_dom] > 0].sort_values(col_dom, ascending=False)
    if pme:
        d = d[d["pme"] == True]
    st.markdown(f"**{fr(len(d))}** acteurs correspondent aux filtres.")
    cols = ["nom", "groupe", "categorie", "ville", "pme", "projets"] + ([col_dom] if col_dom else []) + \
           ["coordinations", "contribution_UE_Meur", "premiere_annee", "derniere_annee"]
    vmax = float(d["contribution_UE_Meur"].max()) if len(d) else 1.0
    sel = st.dataframe(d[cols], hide_index=True, width="stretch", height=480, on_select="rerun",
                       selection_mode="single-row", key="t_act",
                       column_config={"contribution_UE_Meur": st.column_config.ProgressColumn("Contribution (M€)", format="%.2f", min_value=0, max_value=vmax),
                                      "pme": st.column_config.CheckboxColumn("PME"),
                                      "premiere_annee": st.column_config.NumberColumn("De", format="%d"),
                                      "derniere_annee": st.column_config.NumberColumn("À", format="%d")})
    telecharger_excel(d[cols], "acteurs_filtres.xlsx", "Télécharger la sélection (Excel)")
    lignes = sel.selection.rows if sel and sel.selection else []
    if lignes:
        r = d.iloc[lignes[0]]
        st.markdown(f"#### {r['nom']}")
        st.caption(f"{r['categorie']}{' · PME' if r['pme'] else ''} · {r['ville'] or 'ville non renseignée'} · "
                   f"{fr(r['projets'])} projets de {int(r['premiere_annee'])} à {int(r['derniere_annee'])} · {fr(r['contribution_UE_Meur'], 2)} M€")
        rep = pd.DataFrame({"Domaine": list(COLS_DOM.values()), "Projets": [r[c] for c in COLS_DOM]})
        rep = rep[rep["Projets"] > 0].sort_values("Projets")
        fig = px.bar(rep, x="Projets", y="Domaine", orientation="h", text_auto=True, color_discrete_sequence=[BLEU], labels={"Domaine": ""})
        st.plotly_chart(mise_en_forme(fig, 60 + 40 * len(rep)), width="stretch")
    else:
        st.caption("Cliquez sur une ligne pour voir la répartition de l'acteur par domaine.")

# ================================================================ Régions
with t5:
    st.subheader("Acteurs français par région")
    vue = st.radio("Vue", ["Par catégorie d'acteurs", "Acteurs du secteur automobile"], horizontal=True, key="vue_reg")
    cats_reg = [c for c in ["Entreprises", "Organismes de recherche", "Universités et écoles", "Organismes publics", "Autres"] if c in reg]
    if vue.startswith("Par"):
        d = reg.assign(total=reg[cats_reg].sum(axis=1)).sort_values("total")
        fig = px.bar(d, y="region", x=cats_reg, orientation="h", labels={"region": "", "value": "Acteurs distincts", "variable": ""},
                     color_discrete_sequence=[BLEU, VERT, VIOLET, ORANGE, GRIS])
    else:
        d = reg.sort_values("acteurs secteur auto")
        fig = px.bar(d, y="region", x="acteurs secteur auto", orientation="h", text_auto=True, color_discrete_sequence=[BLEU],
                     labels={"region": "", "acteurs secteur auto": "Acteurs du secteur automobile"})
    st.plotly_chart(mise_en_forme(fig, 520), width="stretch")
    st.caption("Selon le siège déclaré dans CORDIS : les grands groupes sont souvent rattachés à l'Île-de-France.")
    st.dataframe(reg, hide_index=True, width="stretch")

# ================================================================ Méthode
with t6:
    a, b = st.columns(2)
    with a:
        st.subheader("Méthode")
        if "Methode" in X:
            for n in X["Methode"].iloc[:, 0]:
                st.markdown(f"- {n}")
    with b:
        st.subheader("Où sont classés les laboratoires clés ?")
        if "Controle_labos" in X:
            st.dataframe(X["Controle_labos"], hide_index=True, width="stretch")
    if "Controle_classement" in X:
        st.subheader("Contrôle du classement par domaine")
        st.caption("Échantillon de projets tirés au hasard par domaine : signalez les projets mal rangés pour ajuster les règles du notebook.")
        ctl = X["Controle_classement"]
        dsel = st.selectbox("Domaine", ["Tous"] + sorted(ctl["domaine"].unique()), key="dom_ctl")
        st.dataframe(ctl if dsel == "Tous" else ctl[ctl["domaine"] == dsel], hide_index=True, width="stretch", height=420)

st.caption("Source : CORDIS (Commission européenne), Horizon 2020 et Horizon Europe, via le notebook Colab « acteurs_FR_projets_europeens ».")
