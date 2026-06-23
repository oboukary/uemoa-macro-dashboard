"""Référentiel des pays de l'UEMOA (Union Économique et Monétaire Ouest-Africaine).

Codes ISO3 utilisés par l'API de la Banque mondiale + métadonnées d'affichage,
y compris les drapeaux (images PNG embarquées dans assets/flags/).
"""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

# Dossier des images de drapeaux : <racine projet>/assets/flags
# (countries.py -> app/utils -> app -> racine)
FLAGS_DIR = Path(__file__).resolve().parents[2] / "assets" / "flags"

# Code ISO3 -> code ISO 3166-1 alpha-2 (nom de fichier du drapeau)
ISO3_TO_ISO2: dict[str, str] = {
    "BEN": "bj", "BFA": "bf", "CIV": "ci", "GNB": "gw",
    "MLI": "ml", "NER": "ne", "SEN": "sn", "TGO": "tg",
}

# Code ISO3 -> métadonnées
UEMOA_COUNTRIES: dict[str, dict[str, str]] = {
    "BEN": {"name": "Bénin", "flag": "🇧🇯", "capital": "Porto-Novo"},
    "BFA": {"name": "Burkina Faso", "flag": "🇧🇫", "capital": "Ouagadougou"},
    "CIV": {"name": "Côte d'Ivoire", "flag": "🇨🇮", "capital": "Yamoussoukro"},
    "GNB": {"name": "Guinée-Bissau", "flag": "🇬🇼", "capital": "Bissau"},
    "MLI": {"name": "Mali", "flag": "🇲🇱", "capital": "Bamako"},
    "NER": {"name": "Niger", "flag": "🇳🇪", "capital": "Niamey"},
    "SEN": {"name": "Sénégal", "flag": "🇸🇳", "capital": "Dakar"},
    "TGO": {"name": "Togo", "flag": "🇹🇬", "capital": "Lomé"},
}

# Nom -> code ISO3 (pratique pour les selectbox)
NAME_TO_ISO3: dict[str, str] = {v["name"]: k for k, v in UEMOA_COUNTRIES.items()}
ISO3_TO_NAME: dict[str, str] = {k: v["name"] for k, v in UEMOA_COUNTRIES.items()}

# Liste ordonnée des codes ISO3 (alphabétique sur le nom)
UEMOA_ISO3: list[str] = sorted(UEMOA_COUNTRIES, key=lambda c: UEMOA_COUNTRIES[c]["name"])
UEMOA_NAMES: list[str] = [UEMOA_COUNTRIES[c]["name"] for c in UEMOA_ISO3]


def iso3_codes() -> list[str]:
    """Retourne la liste des codes ISO3 de l'UEMOA."""
    return list(UEMOA_ISO3)


def name_of(iso3: str) -> str:
    """Nom français d'un pays à partir de son code ISO3."""
    meta = UEMOA_COUNTRIES.get(iso3)
    return meta["name"] if meta else iso3


def flag_of(iso3: str) -> str:
    """Emoji drapeau d'un pays à partir de son code ISO3."""
    meta = UEMOA_COUNTRIES.get(iso3)
    return meta["flag"] if meta else "🏳️"


def label_with_flag(iso3: str) -> str:
    """`🇸🇳 Sénégal` - pratique pour les libellés (emoji, repli)."""
    return f"{flag_of(iso3)} {name_of(iso3)}"


# --- Drapeaux en images (fiables sur tous les OS, contrairement aux emoji) ---

def flag_path(iso3: str) -> Path:
    """Chemin local du PNG du drapeau (utilisable avec st.image)."""
    iso2 = ISO3_TO_ISO2.get(iso3, "")
    return FLAGS_DIR / f"{iso2}.png"


@lru_cache(maxsize=32)
def flag_data_uri(iso3: str) -> str:
    """Drapeau encodé en data URI base64.

    Pratique pour l'injecter dans du HTML (`<img src=...>`) ou dans une
    colonne image d'un tableau Streamlit, sans dépendre d'un serveur de fichiers.
    Renvoie une chaîne vide si l'image est absente.
    """
    path = flag_path(iso3)
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except (FileNotFoundError, OSError):
        return ""


def flag_img_html(iso3: str, height: int = 16) -> str:
    """Balise `<img>` du drapeau (bord arrondi léger), pour le HTML inline."""
    uri = flag_data_uri(iso3)
    if not uri:
        return flag_of(iso3)  # repli emoji
    return (
        f'<img src="{uri}" alt="{name_of(iso3)}" '
        f'style="height:{height}px;border-radius:2px;'
        f'box-shadow:0 0 0 1px rgba(0,0,0,0.08);vertical-align:middle;" />'
    )
