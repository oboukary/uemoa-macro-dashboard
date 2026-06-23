"""Habillage visuel partagé : configuration de page, CSS, en-tête héro, pied."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from utils.config import (
    APP_ICON,
    APP_TAGLINE,
    APP_TITLE,
    ASSETS_DIR,
)
from utils.countries import flag_img_html, name_of

_CSS_FILE = ASSETS_DIR / "styles.css"


def setup_page(subtitle: str | None = None) -> None:
    """Configure la page Streamlit + injecte le CSS. À appeler en tête de chaque page."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()


def inject_css() -> None:
    """Charge assets/styles.css dans la page."""
    try:
        css = Path(_CSS_FILE).read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def hero(title: str, subtitle: str | None = None, pill: str | None = None,
         icon: str | None = None) -> None:
    """Affiche l'en-tête héro coloré en haut d'une page.

    `icon` permet de remplacer l'emoji globe par autre chose (ex. un drapeau
    en `<img>` sur la fiche pays).
    """
    sub = subtitle or APP_TAGLINE
    pill_html = f'<span class="pill">{pill}</span>' if pill else ""
    icon_html = icon if icon is not None else APP_ICON
    st.markdown(
        f"""
        <div class="hero">
            <h1>{icon_html}&nbsp; {title}</h1>
            <p>{sub}</p>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def country_chips(iso3_list: list[str]) -> None:
    """Affiche une rangée de pastilles « drapeau + nom » pour les pays donnés."""
    if not iso3_list:
        return
    chips = "".join(
        f'<span class="country-chip">{flag_img_html(iso3, height=15)}'
        f'<span>{name_of(iso3)}</span></span>'
        for iso3 in iso3_list
    )
    st.markdown(f'<div class="country-chip-row">{chips}</div>',
                unsafe_allow_html=True)


def footer() -> None:
    """Pied de page commun."""
    today = datetime.now().strftime("%d/%m/%Y")
    st.markdown(
        f"""
        <div class="app-footer">
            <strong>{APP_TITLE}</strong> · Données : Banque mondiale (API v2) ·
            Consulté le {today} · Construit avec Streamlit & Plotly.
        </div>
        """,
        unsafe_allow_html=True,
    )
