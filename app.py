TEAM_MEMBERS = ["Alpha Oumar Diallo", "Rokhaya Beye", "Abdourahmane Ndiaye", "Mourtalla Guye", "Serigne Saliou Mbacké"]
CLIENT_NAME = "Atlas Commerce Inc."

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


# Config de page (doit être le premier appel Streamlit)

st.set_page_config(
    page_title="Atlas Commerce | Sales Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Palette & tokens de design

BG = "#0A0E14"
PANEL = "#121821"
PANEL_2 = "#161E29"
BORDER = "#212B38"
TEXT = "#E8EDF2"
MUTED = "#7C8798"
TEAL = "#00D9C0"
TEAL_DIM = "#0A6B60"
CORAL = "#FF6B4A"
AMBER = "#FFB84D"
VIOLET = "#8B7FFF"

CHART_SEQ = [TEAL, CORAL, AMBER, VIOLET, "#4DA6FF", "#FF4D8D"]
CHART_TEMPLATE = "plotly_dark"


def style_fig(fig, height=380):
    """Applique l'identité visuelle commune à tous les graphiques Plotly."""
    fig.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=13),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PANEL_2, font_size=13, font_family="Inter, sans-serif"),
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    return fig



# CSS — identité "salle de contrôle" (fond quasi noir, accent teal,
# chiffres en monospace comme un terminal de trading)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

#MainMenu, footer, header {{visibility: hidden;}}

.stApp {{
    background:
        radial-gradient(ellipse 1200px 600px at 15% -10%, rgba(0,217,192,0.08), transparent),
        radial-gradient(ellipse 900px 500px at 100% 0%, rgba(139,127,255,0.06), transparent),
        {BG};
}}

section[data-testid="stSidebar"] {{
    background: {PANEL};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}

/* Hero band */
.hero {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding: 22px 28px;
    margin-bottom: 18px;
    border-radius: 14px;
    background: linear-gradient(120deg, rgba(0,217,192,0.10), rgba(139,127,255,0.06) 60%, transparent);
    border: 1px solid {BORDER};
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: "";
    position: absolute; top:0; left:0; height:3px; width:100%;
    background: linear-gradient(90deg, {TEAL}, {VIOLET}, {CORAL});
}}
.hero-eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.18em;
    font-size: 11px;
    color: {TEAL};
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: {TEXT};
    line-height: 1.1;
}}
.hero-sub {{
    color: {MUTED};
    font-size: 13.5px;
    margin-top: 6px;
    max-width: 560px;
}}
.hero-meta {{
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {MUTED};
    line-height: 1.6;
}}
.hero-meta b {{ color: {TEXT}; }}

/* Section headers with numbered badges (order = the analysis flow) */
.sec-head {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 26px 0 12px 0;
}}
.sec-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: {BG};
    background: {TEAL};
    border-radius: 6px;
    padding: 3px 8px;
    min-width: 22px;
    text-align: center;
}}
.sec-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px;
    font-weight: 600;
    color: {TEXT};
}}
.sec-line {{
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, {BORDER}, transparent);
}}

/* KPI cards */
.kpi-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: "";
    position: absolute; left:0; top:0; bottom:0; width: 3px;
    background: var(--accent, {TEAL});
}}
.kpi-icon {{ font-size: 18px; opacity: 0.85; }}
.kpi-label {{
    color: {MUTED};
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 6px;
}}
.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: {TEXT};
    margin-top: 2px;
}}
.kpi-delta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    margin-top: 4px;
}}
.kpi-up {{ color: {TEAL}; }}
.kpi-down {{ color: {CORAL}; }}
.kpi-flat {{ color: {MUTED}; }}

/* Panels wrapping charts */
.panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px 16px 4px 16px;
}}
.panel-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 14.5px;
    color: {TEXT};
    margin-bottom: 2px;
}}
.panel-caption {{
    color: {MUTED};
    font-size: 11.5px;
    margin-bottom: 6px;
}}

/* Sidebar headings */
.side-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: {TEXT};
    margin-bottom: 2px;
}}
.side-sub {{
    color: {MUTED};
    font-size: 11px;
    margin-bottom: 14px;
}}
.side-group {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {TEAL};
    margin: 14px 0 4px 0;
}}

.footer-note {{
    text-align: center;
    color: {MUTED};
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 30px;
    padding: 14px 0;
    border-top: 1px solid {BORDER};
}}

div[data-baseweb="tag"] {{
    background-color: {TEAL_DIM} !important;
}}
</style>
""", unsafe_allow_html=True)


# Chargement des données

@st.cache_data
def load_data(path="ventes_enriched.csv"):
    df = pd.read_csv(path, parse_dates=["Order_Date", "Month_Year"])
    return df


df_raw = load_data()

US_STATE_URL = "https://www.axl.cefan.ulaval.ca/amnord/USA_carte_Etats.htm"


# HERO / EN-TÊTE

st.markdown(f"""
<div class="hero">
    <div>
        <div class="hero-eyebrow">● LIVE · SALES INTELLIGENCE</div>
        <div class="hero-title">Atlas Commerce — Pilotage des ventes USA</div>
        <div class="hero-sub">
            Rapport préparé pour <b>{CLIENT_NAME}</b> — analyse des commandes,
            de la clientèle et des performances régionales sur la période sélectionnée.
        </div>
    </div>
    <div class="hero-meta">
        Équipe · {" · ".join(TEAM_MEMBERS)}<br>
        Source · E-commerce Sales Dataset (US)<br>
        Généré · Streamlit + Plotly
    </div>
</div>
""", unsafe_allow_html=True)


# 1. CALENDRIER — sélection de la période de vente

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">1</div>
    <div class="sec-title">Période analysée</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

min_date = df_raw["Order_Date"].min().date()
max_date = df_raw["Order_Date"].max().date()

date_range = st.date_input(
    "Choisissez la période de vente",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="YYYY/MM/DD",
    label_visibility="collapsed",
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

df_period = df_raw[
    (df_raw["Order_Date"].dt.date >= start_date) & (df_raw["Order_Date"].dt.date <= end_date)
]


# 2. FILTRES EN CASCADE — Région > State > Country > City

def cascading_multiselect(label, options, key):
    """Multiselect dont la sélection persistée est nettoyée si les
    options changent (cas des filtres en cascade), pour éviter
    l'erreur Streamlit 'default value is not part of the options'."""
    options = sorted(options)
    if key in st.session_state:
        st.session_state[key] = [v for v in st.session_state[key] if v in options]
    return st.multiselect(label, options=options, key=key, placeholder="Toutes / tous")


with st.sidebar:
    st.markdown('<div class="side-title"> Atlas Commerce</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-sub">Filtres géographiques en cascade</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-group">Choisissez vos filtres</div>', unsafe_allow_html=True)

    region_sel = cascading_multiselect("Région", df_period["Region"].unique(), "f_region")
    df_g1 = df_period[df_period["Region"].isin(region_sel)] if region_sel else df_period

    state_sel = cascading_multiselect("State", df_g1["State_Complet"].unique(), "f_state")
    df_g2 = df_g1[df_g1["State_Complet"].isin(state_sel)] if state_sel else df_g1

    country_sel = cascading_multiselect("Country", df_g2["Country"].unique(), "f_country")
    df_g3 = df_g2[df_g2["Country"].isin(country_sel)] if country_sel else df_g2

    city_sel = cascading_multiselect("City", df_g3["City"].unique(), "f_city")
    df_geo = df_g3[df_g3["City"].isin(city_sel)] if city_sel else df_g3

    st.markdown('<div class="side-group">Reset</div>', unsafe_allow_html=True)
    if st.button("↺ Réinitialiser les filtres", use_container_width=True):
        for k in ["f_region", "f_state", "f_country", "f_city", "f_status"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown(
        f'<div class="side-sub" style="margin-top:18px;">'
        f'{len(df_geo):,} lignes sélectionnées sur {len(df_raw):,} au total'
        f'</div>'.replace(",", " "),
        unsafe_allow_html=True,
    )


# Filtre statut de commande (multiselect, interactif) — placé
# juste avant la ligne des KPI comme demandé dans le brief

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">3</div>
    <div class="sec-title">Indicateurs clés</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

status_sel = cascading_multiselect(
    "Statut de commande", df_geo["Order_Status"].unique(), "f_status"
)
df_f = df_geo[df_geo["Order_Status"].isin(status_sel)] if status_sel else df_geo

if df_f.empty:
    st.warning("Aucune donnée pour cette combinaison de filtres. Élargissez votre sélection.")
    st.stop()

# --- calcul d'une période de référence pour les deltas des KPI ---
period_len = (end_date - start_date).days + 1
prev_start = start_date - timedelta(days=period_len)
prev_end = start_date - timedelta(days=1)
df_prev_period = df_raw[
    (df_raw["Order_Date"].dt.date >= prev_start) & (df_raw["Order_Date"].dt.date <= prev_end)
]
df_prev = df_prev_period
if region_sel:
    df_prev = df_prev[df_prev["Region"].isin(region_sel)]
if state_sel:
    df_prev = df_prev[df_prev["State_Complet"].isin(state_sel)]
if country_sel:
    df_prev = df_prev[df_prev["Country"].isin(country_sel)]
if city_sel:
    df_prev = df_prev[df_prev["City"].isin(city_sel)]
if status_sel:
    df_prev = df_prev[df_prev["Order_Status"].isin(status_sel)]


def delta_pct(curr, prev):
    if prev == 0 or prev is None:
        return None
    return (curr - prev) / prev * 100


def kpi_html(icon, label, value, delta, accent):
    if delta is None:
        delta_html = '<div class="kpi-delta kpi-flat">— pas de période de référence</div>'
    else:
        cls = "kpi-up" if delta > 0 else ("kpi-down" if delta < 0 else "kpi-flat")
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "→")
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% vs période précédente</div>'
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


total_sales = df_f["Total"].sum()
n_customers = df_f["Cust_id"].nunique()
n_orders = df_f["Order_id"].nunique()

prev_sales = df_prev["Total"].sum()
prev_customers = df_prev["Cust_id"].nunique()
prev_orders = df_prev["Order_id"].nunique()

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(kpi_html("", "Nombre total de vente", f"${total_sales:,.0f}".replace(",", " "),
                          delta_pct(total_sales, prev_sales), TEAL), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_html("", "Clients distincts", f"{n_customers:,}".replace(",", " "),
                          delta_pct(n_customers, prev_customers), VIOLET), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_html("", "Commandes distinctes", f"{n_orders:,}".replace(",", " "),
                          delta_pct(n_orders, prev_orders), AMBER), unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# 4. Catégorie (barres) + Région (donut)

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">4</div>
    <div class="sec-title">Ventes par catégorie & répartition régionale</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Ventes totales par catégorie</div>', unsafe_allow_html=True)
    cat_totals = df_f.groupby("Category", as_index=False)["Total"].sum().sort_values("Total", ascending=True)
    fig_cat = px.bar(
        cat_totals, x="Total", y="Category", orientation="h", text="Total",
        color="Total", color_continuous_scale=[PANEL_2, TEAL],
    )
    fig_cat.update_traces(texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False)
    fig_cat.update_layout(coloraxis_showscale=False, xaxis_title="Ventes ($)", yaxis_title="")
    fig_cat = style_fig(fig_cat, height=max(380, 26 * len(cat_totals)))
    fig_cat.update_layout(margin=dict(r=70))
    st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Part des ventes par région</div>', unsafe_allow_html=True)
    reg_totals = df_f.groupby("Region", as_index=False)["Total"].sum().sort_values("Total", ascending=False)
    fig_reg = px.pie(
        reg_totals, names="Region", values="Total", hole=0.58,
        color_discrete_sequence=CHART_SEQ,
    )
    fig_reg.update_traces(textinfo="label+percent", textfont_size=12)
    fig_reg.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig_reg, height=max(380, 26 * len(cat_totals))), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# 5. TOP 10 clients

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">5</div>
    <div class="sec-title">Top 10 des meilleurs clients</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
top10 = (
    df_f.groupby("Full_name", as_index=False)["Total"].sum()
    .sort_values("Total", ascending=False).head(10).sort_values("Total")
)
fig_top10 = px.bar(
    top10, x="Total", y="Full_name", orientation="h", text="Total",
    color="Total", color_continuous_scale=[PANEL_2, TEAL],
)
fig_top10.update_traces(texttemplate="$%{text:,.0f}", textposition="outside", cliponaxis=False)
fig_top10.update_layout(coloraxis_showscale=False, xaxis_title="Ventes ($)", yaxis_title="")
fig_top10 = style_fig(fig_top10, height=420)
fig_top10.update_layout(margin=dict(r=70))
st.plotly_chart(fig_top10, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)


# 6. Âge (histogramme) + Genre (barres + %)

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">6</div>
    <div class="sec-title">Profil démographique des clients</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

customers_unique = df_f.drop_duplicates(subset="Cust_id")

d1, d2 = st.columns(2)
with d1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Répartition de l\'âge des clients</div>', unsafe_allow_html=True)
    fig_age = px.histogram(customers_unique, x="Age", nbins=20, color_discrete_sequence=[TEAL])
    fig_age.update_layout(bargap=0.05, yaxis_title="Nombre de clients", xaxis_title="Âge")
    st.plotly_chart(style_fig(fig_age), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with d2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Répartition Hommes / Femmes</div>', unsafe_allow_html=True)
    gender_counts = customers_unique["Gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "count"]
    gender_counts["pct"] = gender_counts["count"] / gender_counts["count"].sum() * 100
    gender_counts["label"] = gender_counts.apply(lambda r: f"{r['count']} ({r['pct']:.1f}%)", axis=1)
    fig_gender = px.bar(
        gender_counts, x="Gender", y="count", text="label",
        color="Gender", color_discrete_sequence=[TEAL, CORAL],
    )
    fig_gender.update_traces(textposition="outside", cliponaxis=False)
    fig_gender.update_layout(showlegend=False, yaxis_title="Nombre de clients", xaxis_title="")
    st.plotly_chart(style_fig(fig_gender), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# 7. Évolution mensuelle des ventes

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">7</div>
    <div class="sec-title">Évolution mensuelle des ventes</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
monthly = df_f.groupby("Month_Year", as_index=False)["Total"].sum().sort_values("Month_Year")
fig_month = go.Figure()
fig_month.add_trace(go.Scatter(
    x=monthly["Month_Year"], y=monthly["Total"], mode="lines+markers",
    line=dict(color=TEAL, width=2.5), marker=dict(size=5, color=TEAL),
    fill="tozeroy", fillcolor="rgba(0,217,192,0.10)",
    hovertemplate="%{x|%b %Y}<br>Ventes: $%{y:,.0f}<extra></extra>",
))
fig_month.update_layout(xaxis_title="Mois", yaxis_title="Ventes ($)")
st.plotly_chart(style_fig(fig_month, height=380), use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)


# 8. BONUS — Carte des ventes par State

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">8</div>
    <div class="sec-title">Bonus — Ventes totales par State (carte)</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
map_tab1, map_tab2 = st.tabs(["🗺️ Carte choroplèthe", "⚪ Carte à bulles (lat/long)"])

state_totals = df_f.groupby(
    ["State_Code", "State_Complet"], as_index=False
).agg(Total=("Total", "sum"), Latitude=("Latitude", "first"), Longitude=("Longitude", "first"))

with map_tab1:
    fig_map = px.choropleth(
        state_totals, locations="State_Code", locationmode="USA-states",
        color="Total", scope="usa", hover_name="State_Complet",
        color_continuous_scale=["#0F2A28", TEAL],
        labels={"Total": "Ventes ($)"},
    )
    fig_map.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)", landcolor=PANEL_2, lakecolor=BG,
                                    subunitcolor=BORDER))
    st.plotly_chart(style_fig(fig_map, height=480), use_container_width=True, config={"displayModeBar": False})
    st.caption("ℹ️ Les deux cartes ci-dessous chargent leur fond de carte depuis Plotly (CDN) : une connexion internet est nécessaire pour les afficher, comme pour n'importe quelle carte web.")

with map_tab2:
    fig_bubble = px.scatter_geo(
        state_totals, lat="Latitude", lon="Longitude", size="Total",
        color="Total", scope="usa", hover_name="State_Complet",
        color_continuous_scale=["#0F2A28", TEAL], size_max=45,
    )
    fig_bubble.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)", landcolor=PANEL_2, lakecolor=BG,
                                       subunitcolor=BORDER, countrycolor=BORDER))
    st.plotly_chart(style_fig(fig_bubble, height=480), use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)


# BONUS SUPPLÉMENTAIRE — Prévisions de ventes (au-delà du brief)

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">＋</div>
    <div class="sec-title">Bonus — Prévision des ventes à 6 mois</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
if not HAS_STATSMODELS:
    st.info("Installez `statsmodels` (`pip install statsmodels`) pour activer le module de prévision.")
elif len(monthly) < 8:
    st.info("Pas assez de mois de données dans la sélection actuelle pour générer une prévision fiable.")
else:
    horizon = st.slider("Horizon de prévision (mois)", 3, 12, 6)
    ts = monthly.set_index("Month_Year")["Total"].asfreq("MS").fillna(0)
    try:
        model = ExponentialSmoothing(
            ts, trend="add", seasonal="add" if len(ts) >= 24 else None,
            seasonal_periods=12 if len(ts) >= 24 else None,
        ).fit()
        fc = model.forecast(horizon)
        resid_std = np.std(model.resid)

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=ts.index, y=ts.values, mode="lines+markers", name="Historique",
            line=dict(color=TEAL, width=2.5),
        ))
        fig_fc.add_trace(go.Scatter(
            x=fc.index, y=fc.values, mode="lines+markers", name="Prévision",
            line=dict(color=AMBER, width=2.5, dash="dash"),
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(fc.index) + list(fc.index[::-1]),
            y=list(fc.values + 1.96 * resid_std) + list((fc.values - 1.96 * resid_std)[::-1]),
            fill="toself", fillcolor="rgba(255,184,77,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="Intervalle 95%", showlegend=True,
        ))
        fig_fc.update_layout(xaxis_title="Mois", yaxis_title="Ventes ($)",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(style_fig(fig_fc, height=400), use_container_width=True, config={"displayModeBar": False})
        st.caption("Modèle : lissage exponentiel de Holt-Winters (statsmodels). Bande = intervalle de confiance approximatif à 95%.")
    except Exception as e:
        st.warning(f"La prévision n'a pas pu être calculée sur cette sélection ({e}).")
st.markdown('</div>', unsafe_allow_html=True)


# Export des données filtrées

st.markdown("""
<div class="sec-head">
    <div class="sec-badge">⬇</div>
    <div class="sec-title">Export</div>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

exp1, exp2 = st.columns([1, 3])
with exp1:
    st.download_button(
        "⬇ Télécharger la sélection (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="atlas_commerce_export.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp2:
    st.markdown(
        f'<div class="side-sub" style="margin-top:8px;">'
        f'{len(df_f):,} lignes · {n_orders:,} commandes · {n_customers:,} clients'
        f'</div>'.replace(",", " "),
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="footer-note">ATLAS COMMERCE DASHBOARD · Projet Streamlit 2026 · '
    f'{" · ".join(TEAM_MEMBERS)} · Données : E-commerce US Sales</div>',
    unsafe_allow_html=True,
)
