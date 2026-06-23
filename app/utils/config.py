"""Configuration de l'application : chargement du catalogue d'indicateurs,
variables d'environnement et constantes partagées.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Charge .env si présent (développement local). En production (Docker / Cloud),
# les variables sont fournies par l'environnement.
load_dotenv()

# --- Chemins -----------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parents[1]          # .../app
PROJECT_DIR = APP_DIR.parent                            # racine du projet
INDICATORS_FILE = APP_DIR / "data" / "indicators.yml"
ASSETS_DIR = PROJECT_DIR / "assets"

# --- Métadonnées application -------------------------------------------------
APP_TITLE = "UEMOA Macro Dashboard"
APP_ICON = "🌍"
APP_TAGLINE = "Indicateurs macroéconomiques des huit pays de l'UEMOA"
PRIMARY_COLOR = "#0E7C66"   # vert sobre (rappel BCEAO / Afrique de l'Ouest)
ACCENT_COLOR = "#E2A23B"    # accent doré

# Cache des données (en secondes). 6 h par défaut : les séries annuelles
# de la Banque mondiale changent rarement.
CACHE_TTL = int(os.getenv("CACHE_TTL", str(6 * 60 * 60)))

# Clés API optionnelles (V2 : FMI / FRED).
FRED_API_KEY = os.getenv("FRED_API_KEY", "")


@dataclass(frozen=True)
class Indicator:
    """Description d'un indicateur (issue de indicators.yml)."""

    key: str
    code: str
    label: str
    unit: str
    format: str
    category: str
    higher_is_better: bool
    decimals: int
    source: str

    @property
    def label_unit(self) -> str:
        return f"{self.label} ({self.unit})" if self.unit else self.label


@lru_cache(maxsize=1)
def load_indicators() -> dict[str, Indicator]:
    """Charge le catalogue d'indicateurs depuis indicators.yml (mémoïsé)."""
    with open(INDICATORS_FILE, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    indicators: dict[str, Indicator] = {}
    for key, meta in raw.get("indicators", {}).items():
        indicators[key] = Indicator(
            key=key,
            code=meta["code"],
            label=meta["label"],
            unit=meta.get("unit", ""),
            format=meta.get("format", "number"),
            category=meta.get("category", "Autres"),
            higher_is_better=bool(meta.get("higher_is_better", True)),
            decimals=int(meta.get("decimals", 1)),
            source=meta.get("source", "World Bank"),
        )
    return indicators


def indicator_by_code(code: str) -> Indicator | None:
    """Retrouve un indicateur via son code Banque mondiale."""
    for ind in load_indicators().values():
        if ind.code == code:
            return ind
    return None


def categories() -> list[str]:
    """Liste ordonnée des catégories thématiques présentes dans le catalogue."""
    seen: list[str] = []
    for ind in load_indicators().values():
        if ind.category not in seen:
            seen.append(ind.category)
    return seen
