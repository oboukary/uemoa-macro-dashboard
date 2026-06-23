"""UEMOA Macro Dashboard - point d'entrée et navigation.

Ce script est un simple *routeur* : il configure la page, injecte le CSS, puis
délègue l'affichage à la vue sélectionnée via `st.navigation`. Les vues sont
dans `app/views/` et leurs libellés de menu sont définis ci-dessous.

Lancement : `streamlit run app/main.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- Bootstrap des imports ---------------------------------------------------
# Garantit que le dossier `app/` est sur sys.path quelle que soit la façon
# dont Streamlit est lancé (utile pour les imports `utils.*` / `data.*`).
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st  # noqa: E402

from utils.sidebar import sidebar_brand  # noqa: E402
from utils.theme import setup_page  # noqa: E402

# Configuration de page + CSS : une seule fois, dans le routeur.
setup_page()
sidebar_brand()

# Navigation : titres affichés dans la barre latérale.
pages = [
    st.Page("views/accueil.py", title="Accueil", icon="🏠", default=True),
    st.Page("views/comparaison.py", title="Comparaison pays", icon="📊"),
    st.Page("views/fiche_pays.py", title="Fiche pays", icon="📄"),
    st.Page("views/sources.py", title="Sources & méthodologie", icon="📚"),
]

st.navigation(pages).run()
