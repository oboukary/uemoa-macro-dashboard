"""Extraction des indicateurs depuis l'API de la Banque mondiale (v2).

Documentation : https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

Renvoie systématiquement un DataFrame « tidy » :
    country | country_code | year | value | indicator_code | indicator | source
"""

from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from utils.config import CACHE_TTL, load_indicators
from utils.countries import UEMOA_ISO3

BASE_URL = "https://api.worldbank.org/v2"
REQUEST_TIMEOUT = 30


def _build_url(indicator_code: str, iso3_codes: list[str]) -> str:
    countries = ";".join(iso3_codes)
    return (
        f"{BASE_URL}/country/{countries}/indicator/{indicator_code}"
        "?format=json&per_page=20000"
    )


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_indicator(indicator_code: str,
                    iso3_codes: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Récupère une série Banque mondiale pour les pays demandés.

    `iso3_codes` est un tuple (hashable) pour rester compatible avec le cache
    Streamlit. Par défaut : les 8 pays de l'UEMOA.
    """
    codes = list(iso3_codes) if iso3_codes else list(UEMOA_ISO3)
    url = _build_url(indicator_code, codes)

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    # payload[0] = métadonnées de pagination, payload[1] = observations
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return _empty_frame()

    indicators = load_indicators()
    label = next(
        (ind.label for ind in indicators.values() if ind.code == indicator_code),
        indicator_code,
    )

    rows = []
    for item in payload[1]:
        rows.append({
            "country": item["country"]["value"],
            "country_code": item.get("countryiso3code") or item["country"].get("id"),
            "year": int(item["date"]),
            "value": item["value"],
            "indicator_code": indicator_code,
            "indicator": label,
            "source": "World Bank",
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return _empty_frame()

    # Nettoyage : on garde les valeurs renseignées, types corrects.
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).sort_values(["country", "year"])
    return df.reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_many(indicator_codes: tuple[str, ...],
               iso3_codes: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Concatène plusieurs indicateurs dans un seul DataFrame long."""
    frames = [fetch_indicator(code, iso3_codes) for code in indicator_codes]
    frames = [f for f in frames if not f.empty]
    if not frames:
        return _empty_frame()
    return pd.concat(frames, ignore_index=True)


def latest_values(df: pd.DataFrame) -> pd.DataFrame:
    """Dernière valeur disponible par pays (utile pour KPI et classements)."""
    if df.empty:
        return df
    idx = df.groupby("country_code")["year"].idxmax()
    return df.loc[idx].sort_values("country").reset_index(drop=True)


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "country", "country_code", "year", "value",
        "indicator_code", "indicator", "source",
    ])
