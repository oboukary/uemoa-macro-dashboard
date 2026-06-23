"""Page : Sources des données & méthodologie."""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from data.extract_fred import is_configured as fred_ready  # noqa: E402
from utils.config import load_indicators  # noqa: E402
from utils.countries import UEMOA_COUNTRIES, flag_data_uri  # noqa: E402
from utils.theme import footer, hero  # noqa: E402

hero(
    "Sources & méthodologie",
    "Provenance des données, indicateurs disponibles et limites d'interprétation.",
    pill="transparence",
)

# --- Sources -----------------------------------------------------------------
st.subheader("Sources de données")

st.markdown(
    """
| Source | Statut | Couverture |
|---|---|---|
| **Banque mondiale** (API v2) | ✅ Active (V1) | PIB, inflation, population, dette, commerce, social |
| **FMI / WEO** (DataMapper) | 🧩 Intégrée (V2) | Prévisions, solde budgétaire, compte courant, dette publique |
| **FRED** (St. Louis Fed) | {fred} | Contexte mondial : pétrole, dollar, taux Fed, prix US |
| BCEAO / UEMOA / BOAD | 🔜 Prévu | Données régionales spécifiques |
""".format(fred="🔑 Clé API requise" if not fred_ready() else "✅ Active")
)

st.info(
    "Les pays sont identifiés par leur code **ISO 3166-1 alpha-3**, commun à la "
    "Banque mondiale et au FMI, ce qui permet de croiser les sources sans ambiguïté."
)

# --- Pays couverts -----------------------------------------------------------
st.subheader("Pays couverts (UEMOA)")
countries_df = pd.DataFrame(
    [
        {
            "Drapeau": flag_data_uri(code),
            "Pays": m["name"],
            "Code ISO3": code,
            "Capitale": m["capital"],
        }
        for code, m in UEMOA_COUNTRIES.items()
    ]
).sort_values("Pays")
st.dataframe(
    countries_df,
    width="stretch",
    hide_index=True,
    column_config={
        "Drapeau": st.column_config.ImageColumn("Drapeau", width="small"),
    },
)

# --- Catalogue d'indicateurs -------------------------------------------------
st.subheader("Catalogue d'indicateurs")
indicators = load_indicators()
ind_df = pd.DataFrame(
    [
        {
            "Indicateur": ind.label,
            "Code BM": ind.code,
            "Unité": ind.unit,
            "Catégorie": ind.category,
            "Source": ind.source,
        }
        for ind in indicators.values()
    ]
)
st.dataframe(ind_df, width="stretch", hide_index=True)

# --- Méthodologie ------------------------------------------------------------
st.subheader("Méthodologie & limites")
st.markdown(
    """
- **Fraîcheur** : les séries de la Banque mondiale sont annuelles ; la dernière
  année disponible varie selon le pays et l'indicateur (souvent N-1 ou N-2).
- **Valeurs manquantes** : les observations vides sont retirées avant calcul ;
  un classement « dernière année » peut donc comparer des millésimes différents.
- **Cache** : les appels API sont mis en cache (6 h par défaut) pour limiter la
  charge réseau. Modifiable via la variable d'environnement `CACHE_TTL`.
- **Comparabilité** : certains indicateurs en USD courant ne sont pas corrigés de
  l'inflation ni des taux de change - à interpréter avec prudence dans le temps.
- **Source primaire** : toujours se référer aux publications officielles
  (BCEAO, FMI Article IV, comptes nationaux) pour une analyse engageante.
"""
)

footer()
