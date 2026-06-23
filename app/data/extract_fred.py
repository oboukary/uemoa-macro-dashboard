"""Extraction depuis l'API FRED (Federal Reserve Bank of St. Louis).

Utile pour le CONTEXTE GLOBAL (V2) : taux Fed, prix du pétrole, indice dollar,
inflation US, matières premières — variables qui influencent les économies UEMOA.

Nécessite une clé API gratuite : https://fred.stlouisfed.org/docs/api/api_key.html
À renseigner dans la variable d'environnement FRED_API_KEY (voir .env.example).

Statut : opérationnel si une clé est fournie ; sinon les fonctions renvoient un
DataFrame vide sans lever d'erreur.
"""

from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from utils.config import CACHE_TTL, FRED_API_KEY

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
REQUEST_TIMEOUT = 30

# Quelques séries de contexte mondial pertinentes pour l'UEMOA.
CONTEXT_SERIES: dict[str, str] = {
    "DCOILBRENTEU": "Pétrole Brent (USD/baril)",
    "DTWEXBGS": "Indice dollar US (large)",
    "FEDFUNDS": "Taux directeur Fed (%)",
    "CPIAUCSL": "Indice des prix US (CPI)",
    "PCOTTINDUSDM": "Coton (indice prix mondial)",
}


def is_configured() -> bool:
    """Vrai si une clé API FRED est disponible."""
    return bool(FRED_API_KEY)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_series(series_id: str, start: str = "2000-01-01") -> pd.DataFrame:
    """Récupère les observations d'une série FRED.

    Renvoie : date | value | series_id | label | source
    """
    if not is_configured():
        return _empty_frame()

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
    }
    response = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    observations = response.json().get("observations", [])

    rows = []
    for obs in observations:
        val = obs.get("value")
        if val in (None, ".", ""):
            continue
        rows.append({
            "date": pd.to_datetime(obs["date"]),
            "value": float(val),
            "series_id": series_id,
            "label": CONTEXT_SERIES.get(series_id, series_id),
            "source": "FRED",
        })
    df = pd.DataFrame(rows)
    return df if not df.empty else _empty_frame()


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["date", "value", "series_id", "label", "source"])
