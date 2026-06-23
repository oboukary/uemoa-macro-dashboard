"""Fabriques de graphiques Plotly avec un style cohérent pour le dashboard."""

from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.config import ACCENT_COLOR, PRIMARY_COLOR
from utils.countries import UEMOA_ISO3, name_of

# Palette qualitative (8 pays UEMOA)
UEMOA_PALETTE = [
    "#0E7C66", "#E2A23B", "#2D6A9F", "#C0504D",
    "#7E57C2", "#3FA796", "#D77A61", "#5B8C5A",
]

_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Inter, Segoe UI, system-ui, sans-serif", size=13, color="#1A1A2E"),
    margin=dict(l=10, r=10, t=90, b=10),
    # title_text="" supprime le libellé technique "country" au-dessus de la légende.
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                title_text=""),
    hoverlabel=dict(font_size=12),
    colorway=UEMOA_PALETTE,
)


def _apply(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(**_LAYOUT)
    if title:
        # Placement automatique du titre dans la marge haute (au-dessus de la légende).
        fig.update_layout(title=dict(text=title, x=0, xanchor="left",
                                     font=dict(size=17, color=PRIMARY_COLOR)))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EAEFF2", zeroline=False)
    return fig


def line_by_country(df: pd.DataFrame, *, title: str | None = None,
                    y_title: str = "") -> go.Figure:
    """Évolution temporelle d'un indicateur, une courbe par pays."""
    fig = px.line(
        df.sort_values("year"),
        x="year", y="value", color="country",
        markers=True,
    )
    fig.update_traces(line=dict(width=2.2), marker=dict(size=5))
    fig.update_yaxes(title_text=y_title)
    fig.update_xaxes(title_text="")
    return _apply(fig, title)


def small_multiples(df: pd.DataFrame, *, title: str | None = None,
                    y_title: str = "", n_cols: int = 4) -> go.Figure:
    """Petits multiples : un panneau par pays, axes partagés.

    La **médiane régionale** (toutes années) est tracée en gris derrière chaque
    courbe pour situer chaque pays par rapport à l'ensemble de l'UEMOA. Une ligne
    pointillée à zéro facilite la lecture des valeurs négatives.
    """
    if df.empty:
        return _apply(go.Figure(), title)

    # Ordre UEMOA (français), en ne gardant que les pays présents.
    present = set(df["country_code"].unique())
    codes = [c for c in UEMOA_ISO3 if c in present]
    titles = [name_of(c) for c in codes]

    # Médiane régionale par année (ligne de contexte commune à tous les panneaux).
    median = df.groupby("year")["value"].median().reset_index().sort_values("year")

    n = len(codes)
    n_rows = math.ceil(n / n_cols)
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=titles,
        shared_yaxes=True, shared_xaxes=True,
        horizontal_spacing=0.025, vertical_spacing=0.16,
    )

    for i, code in enumerate(codes):
        r, c = i // n_cols + 1, i % n_cols + 1
        cdf = df[df["country_code"] == code].sort_values("year")

        # Médiane régionale (fond gris)
        fig.add_trace(
            go.Scatter(
                x=median["year"], y=median["value"], mode="lines",
                line=dict(color="rgba(120,130,128,0.40)", width=1.1),
                hoverinfo="skip", showlegend=False,
            ),
            row=r, col=c,
        )
        # Courbe du pays (couleur principale + aire légère)
        fig.add_trace(
            go.Scatter(
                x=cdf["year"], y=cdf["value"], mode="lines",
                line=dict(color=PRIMARY_COLOR, width=2),
                fill="tozeroy", fillcolor="rgba(14,124,102,0.07)",
                name=name_of(code), showlegend=False,
                hovertemplate="%{x} : %{y:.1f}<extra></extra>",
            ),
            row=r, col=c,
        )
        # Repère à zéro
        fig.add_hline(y=0, line=dict(color="#D6DEDB", width=1, dash="dot"),
                      row=r, col=c)

    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, system-ui, sans-serif",
                  size=12, color="#1A1A2E"),
        margin=dict(l=10, r=10, t=70, b=10),
        height=170 * n_rows + 70,
        colorway=UEMOA_PALETTE,
    )
    if title:
        fig.update_layout(title=dict(text=title, x=0, xanchor="left",
                                     font=dict(size=17, color=PRIMARY_COLOR)))
    # Titres de panneaux plus discrets
    fig.update_annotations(font=dict(size=12.5, color="#103a32"))
    fig.update_xaxes(showgrid=False, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#EAEFF2", zeroline=False, tickfont=dict(size=10))
    # Libellé d'axe Y uniquement sur la première colonne
    for row in range(1, n_rows + 1):
        fig.update_yaxes(title_text=y_title, row=row, col=1, title_font=dict(size=11))
    return fig


def bar_latest(df: pd.DataFrame, *, title: str | None = None,
               y_title: str = "") -> go.Figure:
    """Classement des pays sur la dernière année disponible."""
    data = df.sort_values("value", ascending=True)
    fig = px.bar(data, x="value", y="country", orientation="h",
                 text="value", color="value",
                 color_continuous_scale=["#CDE3DC", PRIMARY_COLOR])
    fig.update_traces(texttemplate="%{text:.4s}", textposition="outside",
                      cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title_text=y_title)
    fig.update_yaxes(title_text="")
    return _apply(fig, title)


def line_single(df: pd.DataFrame, *, title: str | None = None,
                y_title: str = "", color: str = PRIMARY_COLOR) -> go.Figure:
    """Série unique (fiche pays) avec aire légère."""
    data = df.sort_values("year")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["year"], y=data["value"], mode="lines+markers",
        line=dict(width=2.6, color=color),
        marker=dict(size=6, color=color),
        fill="tozeroy", fillcolor="rgba(14,124,102,0.08)",
        name=y_title or "valeur",
    ))
    fig.update_yaxes(title_text=y_title)
    return _apply(fig, title)


def grouped_bar(df: pd.DataFrame, *, x: str, y: str, color: str,
                title: str | None = None, y_title: str = "") -> go.Figure:
    """Barres groupées (comparaison multi-pays / multi-années)."""
    fig = px.bar(df, x=x, y=y, color=color, barmode="group")
    fig.update_yaxes(title_text=y_title)
    fig.update_xaxes(title_text="")
    return _apply(fig, title)
