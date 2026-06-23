"""Vue Accueil : panorama régional de l'UEMOA (un indicateur, 8 pays)."""

from __future__ import annotations

import sys
from pathlib import Path

# --- Bootstrap des imports ---------------------------------------------------
# Garantit que le dossier `app/` est sur sys.path quelle que soit la façon
# dont Streamlit est lancé (utile pour les imports `utils.*` / `data.*`).
APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from data.extract_worldbank import fetch_indicator, latest_values  # noqa: E402
from utils.charts import bar_latest, small_multiples  # noqa: E402
from utils.countries import UEMOA_ISO3  # noqa: E402
from utils.format import format_value  # noqa: E402
from utils.sidebar import indicator_selector  # noqa: E402
from utils.theme import country_chips, footer, hero  # noqa: E402

hero(
    "Vue régionale",
    "Panorama macroéconomique des huit pays de l'UEMOA - source Banque mondiale.",
    pill="8 pays · données annuelles",
)

# Rangée de drapeaux des 8 pays membres
country_chips(list(UEMOA_ISO3))

# --- Sélection ---------------------------------------------------------------
indicator = indicator_selector()
st.sidebar.markdown("---")
st.sidebar.caption(
    "💡 Naviguez entre les pages dans le menu ci-dessus : "
    "comparaison, fiche pays, sources."
)

# --- Données -----------------------------------------------------------------
with st.spinner("Chargement des données Banque mondiale…"):
    df = fetch_indicator(indicator.code, tuple(UEMOA_ISO3))

if df.empty:
    st.warning(
        f"Aucune donnée disponible pour « {indicator.label} ». "
        "Essayez un autre indicateur."
    )
    footer()
    st.stop()

latest = latest_values(df)
latest_year = int(df["year"].max())
latest_for_year = df[df["year"] == latest_year]

# --- KPI ---------------------------------------------------------------------
st.subheader(f"{indicator.label} - synthèse")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Dernière année", latest_year)
c2.metric("Pays couverts", int(latest["country_code"].nunique()))

region_mean = latest["value"].mean()
c3.metric(
    "Moyenne régionale",
    format_value(region_mean, indicator.format, indicator.unit, indicator.decimals),
)

top = latest.loc[latest["value"].idxmax()]
c4.metric(
    "Valeur la plus élevée",
    format_value(top["value"], indicator.format, indicator.unit, indicator.decimals),
    help=f"{top['country']} ({int(top['year'])})",
)

st.markdown("")

# --- Visualisations ----------------------------------------------------------
tab_evo, tab_rank, tab_data = st.tabs(
    ["📈 Évolution", "🏆 Classement", "🗂️ Données"]
)

with tab_evo:
    fig = small_multiples(
        df,
        title=f"{indicator.label} - évolution par pays",
        y_title=indicator.unit,
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Un panneau par pays (axes partagés). La **ligne grise** rappelle la "
        "médiane régionale UEMOA ; la **ligne pointillée** marque le zéro."
    )

with tab_rank:
    # Année réelle (ou plage si les pays n'ont pas tous le même millésime).
    yrs = latest["year"]
    ymin, ymax = int(yrs.min()), int(yrs.max())
    year_label = str(ymax) if ymin == ymax else f"{ymin}-{ymax}"
    fig = bar_latest(
        latest,
        title=f"{indicator.label} - par pays ({year_label})",
        y_title=indicator.unit,
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Chaque barre correspond à la dernière année renseignée pour le pays "
        "(elle peut différer d'un pays à l'autre)."
    )

with tab_data:
    show = df[["country", "year", "value", "indicator", "source"]].copy()
    show = show.rename(columns={
        "country": "Pays", "year": "Année", "value": "Valeur",
        "indicator": "Indicateur", "source": "Source",
    })
    st.dataframe(show, width="stretch", hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Exporter en CSV",
        data=csv,
        file_name=f"uemoa_{indicator.key}.csv",
        mime="text/csv",
    )

footer()
