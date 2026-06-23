"""Page : Fiche détaillée d'un pays (tableau de bord macro mono-pays)."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st  # noqa: E402

from data.extract_worldbank import fetch_indicator  # noqa: E402
from utils.charts import line_single  # noqa: E402
from utils.config import load_indicators  # noqa: E402
from utils.countries import (  # noqa: E402
    UEMOA_COUNTRIES,
    flag_img_html,
    name_of,
)
from utils.format import format_delta, format_value  # noqa: E402
from utils.sidebar import country_selector  # noqa: E402
from utils.theme import footer, hero  # noqa: E402

# Indicateurs mis en avant sur la fiche (clés de indicators.yml)
FEATURED = [
    "gdp_growth", "inflation", "gdp_per_capita",
    "population", "gov_debt_gdp", "current_account_gdp",
]

iso3 = country_selector(key="fiche_country")
meta = UEMOA_COUNTRIES.get(iso3, {})
indicators = load_indicators()

# Pré-chargement des séries (réutilisées pour les KPI et les graphiques) afin
# de connaître la dernière année disponible avant d'afficher l'en-tête.
series_cache: dict[str, "object"] = {}
for key in FEATURED:
    ind = indicators.get(key)
    if ind is not None:
        series_cache[key] = fetch_indicator(ind.code, (iso3,))

available_years = [
    int(df["year"].max()) for df in series_cache.values() if not df.empty
]
latest_year = max(available_years) if available_years else None
year_label = f" {latest_year}" if latest_year else ""

hero(
    name_of(iso3),
    f"Fiche macroéconomique{year_label} — capitale : {meta.get('capital', '—')}.",
    pill="fiche pays",
    icon=flag_img_html(iso3, height=34),
)

# --- Cartes KPI (dernière valeur + variation) --------------------------------
st.subheader("Indicateurs clés")
cols = st.columns(3)

for i, key in enumerate(FEATURED):
    ind = indicators.get(key)
    if ind is None:
        continue
    df = series_cache.get(key)
    col = cols[i % 3]
    if df is None or df.empty:
        col.metric(ind.label, "—")
        continue
    df = df.sort_values("year")
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    delta = format_delta(last["value"], prev["value"] if prev is not None else None,
                         ind.format, ind.decimals)
    col.metric(
        f"{ind.label}",
        format_value(last["value"], ind.format, ind.unit, ind.decimals),
        delta=delta,
        help=f"Dernière année : {int(last['year'])}",
    )

st.markdown("---")

# --- Petits graphiques (small multiples) -------------------------------------
st.subheader("Évolution")
chart_cols = st.columns(2)
for i, key in enumerate(FEATURED):
    ind = indicators.get(key)
    if ind is None:
        continue
    df = series_cache.get(key)
    if df is None:
        df = fetch_indicator(ind.code, (iso3,))
    if df is None or df.empty:
        continue
    with chart_cols[i % 2]:
        st.plotly_chart(
            line_single(df, title=ind.label, y_title=ind.unit),
            width="stretch",
        )

footer()
