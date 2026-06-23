"""Page : Comparaison entre pays de l'UEMOA sur un indicateur donné."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st  # noqa: E402

from data.extract_worldbank import fetch_indicator, latest_values  # noqa: E402
from utils.charts import bar_latest, line_by_country  # noqa: E402
from utils.countries import flag_path  # noqa: E402
from utils.format import format_value  # noqa: E402
from utils.sidebar import (  # noqa: E402
    country_multiselect,
    indicator_selector,
    sidebar_brand,
)
from utils.theme import country_chips, footer, hero, setup_page  # noqa: E402

setup_page()
sidebar_brand()
hero(
    "Comparaison pays",
    "Comparez les trajectoires de plusieurs pays sur un même indicateur.",
    pill="comparaison multi-pays",
)

indicator = indicator_selector(key="cmp_indicator")
countries = country_multiselect(key="cmp_countries")

# Drapeaux des pays sélectionnés
country_chips(countries)

with st.spinner("Chargement…"):
    df = fetch_indicator(indicator.code, tuple(countries))

if df.empty:
    st.warning("Aucune donnée pour cette sélection.")
    footer()
    st.stop()

# Bornes temporelles
year_min, year_max = int(df["year"].min()), int(df["year"].max())
if year_min < year_max:
    start, end = st.slider(
        "Période",
        min_value=year_min, max_value=year_max,
        value=(max(year_min, year_max - 20), year_max),
    )
    df = df[(df["year"] >= start) & (df["year"] <= end)]

latest = latest_values(df)

st.subheader(f"{indicator.label}")

# Mini-classement en cartes
if not latest.empty:
    cols = st.columns(min(len(latest), 4))
    ranked = latest.sort_values("value", ascending=not indicator.higher_is_better)
    for i, (_, row) in enumerate(ranked.head(len(cols)).iterrows()):
        cols[i].image(str(flag_path(row["country_code"])), width=30)
        cols[i].metric(
            row["country"],
            format_value(row["value"], indicator.format, indicator.unit, indicator.decimals),
            help=f"Année {int(row['year'])}",
        )

tab_evo, tab_rank, tab_data = st.tabs(["📈 Évolution", "🏆 Classement", "🗂️ Données"])

with tab_evo:
    st.plotly_chart(
        line_by_country(df, title=f"{indicator.label} — évolution comparée",
                        y_title=indicator.unit),
        width="stretch",
    )

with tab_rank:
    st.plotly_chart(
        bar_latest(latest, title=f"{indicator.label} — dernière valeur par pays",
                   y_title=indicator.unit),
        width="stretch",
    )

with tab_data:
    pivot = df.pivot_table(index="year", columns="country", values="value")
    st.dataframe(pivot, width="stretch")
    st.download_button(
        "⬇️ Exporter en CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"uemoa_comparaison_{indicator.key}.csv",
        mime="text/csv",
    )

footer()
