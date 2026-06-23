"""Extraction depuis l'API du FMI (Fonds Monétaire International).

Cible (V2) : World Economic Outlook (WEO) et indicateurs IFS - solde budgétaire,
compte courant, dette publique, prévisions macro.

Le FMI expose plusieurs API. Cette implémentation utilise l'API DataMapper v1
(https://www.imf.org/external/datamapper/api/help), simple et sans clé, qui
fournit les séries WEO par pays.

Statut : opérationnel pour les indicateurs DataMapper listés ci-dessous.
Les pays sont adressés par code ISO3 (mêmes codes que la Banque mondiale).
"""

from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from utils.config import CACHE_TTL
from utils.countries import UEMOA_ISO3

BASE_URL = "https://www.imf.org/external/datamapper/api/v1"
REQUEST_TIMEOUT = 30

# Indicateurs DataMapper du FMI (clé interne -> code FMI + libellé).
IMF_INDICATORS: dict[str, dict[str, str]] = {
    "ngdp_rpch": {"code": "NGDP_RPCH", "label": "Croissance du PIB réel (%) - WEO"},
    "pcpipch": {"code": "PCPIPCH", "label": "Inflation moyenne (%) - WEO"},
    "ggxwdg_ngdp": {"code": "GGXWDG_NGDP", "label": "Dette publique brute (% PIB) - WEO"},
    "ggxcnl_ngdp": {"code": "GGXCNL_NGDP", "label": "Solde budgétaire (% PIB) - WEO"},
    "bca_ngdpd": {"code": "BCA_NGDPD", "label": "Solde courant (% PIB) - WEO"},
}


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_indicator(imf_code: str,
                    iso3_codes: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Récupère une série WEO via DataMapper.

    Renvoie : country_code | year | value | indicator_code | indicator | source
    """
    codes = list(iso3_codes) if iso3_codes else list(UEMOA_ISO3)
    url = f"{BASE_URL}/{imf_code}/" + "/".join(codes)

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    values = payload.get("values", {}).get(imf_code, {})
    label = next(
        (m["label"] for m in IMF_INDICATORS.values() if m["code"] == imf_code),
        imf_code,
    )

    wanted = set(codes)
    rows = []
    for iso3, series in values.items():
        # DataMapper ignore parfois le filtre pays de l'URL : on filtre ici.
        if iso3 not in wanted:
            continue
        for year, value in series.items():
            if value is None:
                continue
            rows.append({
                "country_code": iso3,
                "year": int(year),
                "value": float(value),
                "indicator_code": imf_code,
                "indicator": label,
                "source": "IMF (WEO)",
            })
    df = pd.DataFrame(rows)
    return df if not df.empty else _empty_frame()


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "country_code", "year", "value", "indicator_code", "indicator", "source",
    ])
