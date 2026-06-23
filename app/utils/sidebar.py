"""Composants de barre latérale réutilisés sur toutes les pages."""

from __future__ import annotations

import streamlit as st

from utils.config import Indicator, categories, load_indicators
from utils.countries import UEMOA_ISO3, flag_img_html, name_of


def sidebar_brand() -> None:
    """Bloc de marque en haut de la barre latérale."""
    st.sidebar.markdown(
        """
        <div style="padding:0.4rem 0 1rem;">
            <div style="font-size:1.35rem;font-weight:700;">🌍 UEMOA</div>
            <div style="font-size:0.8rem;opacity:0.8;">Macro Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def indicator_selector(key: str = "indicator",
                       default_key: str = "gdp_growth") -> Indicator:
    """Sélecteur d'indicateur regroupé par catégorie."""
    indicators = load_indicators()

    # Construit la liste "Catégorie — Libellé" ordonnée par catégorie.
    options: list[str] = []
    label_to_key: dict[str, str] = {}
    for cat in categories():
        for ikey, ind in indicators.items():
            if ind.category == cat:
                display = f"{ind.label}"
                options.append(display)
                label_to_key[display] = ikey

    default_label = indicators[default_key].label if default_key in indicators else options[0]
    default_index = options.index(default_label) if default_label in options else 0

    chosen = st.sidebar.selectbox("Indicateur", options, index=default_index, key=key)
    return indicators[label_to_key[chosen]]


def country_multiselect(key: str = "countries",
                        default_all: bool = True) -> list[str]:
    """Sélection multiple de pays (renvoie des codes ISO3)."""
    default = list(UEMOA_ISO3) if default_all else list(UEMOA_ISO3[:4])
    chosen_names = st.sidebar.multiselect(
        "Pays",
        options=[name_of(c) for c in UEMOA_ISO3],
        default=[name_of(c) for c in default],
        format_func=lambda n: n,
        key=key,
    )
    name_to_iso = {name_of(c): c for c in UEMOA_ISO3}
    return [name_to_iso[n] for n in chosen_names] or list(UEMOA_ISO3)


def country_selector(key: str = "country", default: str = "BFA") -> str:
    """Sélection d'un pays unique (fiche pays). Renvoie un code ISO3.

    Le menu déroulant affiche les noms (les emoji ne s'affichent pas partout) ;
    le pays sélectionné est rappelé en dessous avec son **vrai drapeau avant
    son nom**.
    """
    options = list(UEMOA_ISO3)
    index = options.index(default) if default in options else 0
    iso3 = st.sidebar.selectbox(
        "Pays",
        options,
        index=index,
        format_func=name_of,
        key=key,
    )
    st.sidebar.markdown(
        f'<div class="sidebar-country">{flag_img_html(iso3, height=18)}'
        f'<span>{name_of(iso3)}</span></div>',
        unsafe_allow_html=True,
    )
    return iso3
