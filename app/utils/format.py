"""Helpers de formatage des valeurs numériques (libellés courts FR)."""

from __future__ import annotations

import math


def _is_missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def human_number(value: float, decimals: int = 1) -> str:
    """Formate un grand nombre en notation courte : 1 234 567 -> 1,23 M."""
    if _is_missing(value):
        return "n.d."
    value = float(value)
    sign = "-" if value < 0 else ""
    n = abs(value)
    for threshold, suffix in ((1e12, " Bn"), (1e9, " Md"), (1e6, " M"), (1e3, " k")):
        if n >= threshold:
            return f"{sign}{n / threshold:,.2f}{suffix}".replace(",", " ")
    return f"{sign}{n:,.{decimals}f}".replace(",", " ")


def format_value(value, fmt: str = "number", unit: str = "", decimals: int = 1) -> str:
    """Formate une valeur selon le type d'indicateur."""
    if _is_missing(value):
        return "n.d."
    value = float(value)

    if fmt == "percent":
        return f"{value:,.{decimals}f} %".replace(",", " ")
    if fmt == "currency":
        return f"{human_number(value, decimals)} $"
    if fmt == "people":
        return human_number(value, 0)
    # number générique
    suffix = f" {unit}" if unit and unit not in {"%", "USD"} else ""
    return f"{value:,.{decimals}f}{suffix}".replace(",", " ")


def format_delta(current, previous, fmt: str = "number", decimals: int = 1) -> str | None:
    """Variation entre deux valeurs, prête pour st.metric(delta=...)."""
    if _is_missing(current) or _is_missing(previous):
        return None
    current, previous = float(current), float(previous)
    if fmt in {"percent"}:
        # variation en points de pourcentage
        return f"{current - previous:+.{decimals}f} pts"
    if previous == 0:
        return None
    pct = (current - previous) / abs(previous) * 100
    return f"{pct:+.1f} %"
