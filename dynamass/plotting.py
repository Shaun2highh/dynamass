"""Figures. Tokens follow the validated reference palette (light mode)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from .system import System, mass_factor_to_inclination_deg

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SERIES_1 = "#2a78d6"  # blue
SERIES_6 = "#e34948"  # red — reserved here for the instability side
BLUE_LIGHT = "#9ec5f4"  # sequential step 200: the floor→ceiling span
BLUE_DARK = "#104281"  # sequential step 650: the ceiling end


def _style_axes(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelcolor=INK_SECONDARY)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_survival_curve(
    curve: pd.DataFrame,
    system: System,
    t_max_yr: float,
    ceiling: float | None,
    path: str,
) -> None:
    """Survival fraction vs true-mass factor for one system's coplanar sweep."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)

    df = curve.sort_values("mass_factor")
    ax.plot(
        df["mass_factor"],
        df["survival_fraction"],
        color=SERIES_1,
        linewidth=2,
        marker="o",
        markersize=5,
        markerfacecolor=SERIES_1,
        markeredgecolor=SURFACE,
        markeredgewidth=1,
        zorder=3,
    )

    if ceiling is not None:
        ax.axvline(ceiling, color=SERIES_6, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
        ax.annotate(
            f"dynamical ceiling\nm < {ceiling:.1f} x msini",
            xy=(ceiling, 0.78),
            xytext=(ceiling * 1.12, 0.78),
            color=SERIES_6,
            fontsize=9,
            va="center",
        )

    ax.set_xscale("log")
    ticks = [1, 1.5, 2, 3, 5, 8, 12]
    ticks = [t for t in ticks if t <= df["mass_factor"].max() * 1.05]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}x" for t in ticks])
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("true mass / minimum mass  (= 1 / sin i)", color=INK_SECONDARY)
    ax.set_ylabel(f"survival fraction ({t_max_yr:,.0f} yr)", color=INK_SECONDARY)

    sec = ax.secondary_xaxis("top")
    sec.set_xticks(ticks)
    sec.set_xticklabels([f"{mass_factor_to_inclination_deg(t):.0f}°" for t in ticks])
    sec.tick_params(colors=MUTED, labelcolor=MUTED)
    sec.spines["top"].set_visible(False)
    sec.set_xlabel("line-of-sight inclination", color=MUTED, fontsize=9)

    ax.set_title(
        f"{system.name}: dynamics as a scale",
        color=INK,
        fontsize=12,
        loc="left",
        pad=24,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


BLUE_SHALLOW = "#86b6ef"  # sequential step 250: the shallow-depth ceiling
DEUTERIUM_LIMIT_MJUP = 13.0


def plot_depth_convergence(
    cmp: pd.DataFrame,
    labels: tuple[str, str],
    sweep_max: float,
    path: str,
) -> None:
    """Ceiling factor per system at two integration depths.

    cmp is indexed by system with columns f_shallow and f_deep; NaN means no
    ceiling inside the swept range, drawn as an open marker at the sweep edge
    (the constraint there is "ceiling > sweep_max").
    """
    df = cmp[cmp["f_deep"].notna()].sort_values("f_deep").copy()
    if df.empty:
        return
    shallow = df["f_shallow"].fillna(sweep_max)
    open_marker = df["f_shallow"].isna()

    fig, ax = plt.subplots(figsize=(7.5, 1.4 + 0.32 * len(df)), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)
    ax.grid(axis="y", visible=False)

    y = np.arange(len(df))
    ax.hlines(y, df["f_deep"], shallow, color=GRID, linewidth=1.2, zorder=2)
    ax.scatter(
        shallow[~open_marker],
        y[~open_marker.values],
        s=28,
        color=BLUE_SHALLOW,
        zorder=3,
        edgecolors=SURFACE,
        linewidths=0.8,
        label=labels[0],
    )
    ax.scatter(
        shallow[open_marker],
        y[open_marker.values],
        s=28,
        facecolors="none",
        edgecolors=BLUE_SHALLOW,
        linewidths=1.2,
        zorder=3,
    )
    ax.scatter(
        df["f_deep"],
        y,
        s=28,
        color=BLUE_DARK,
        zorder=4,
        edgecolors=SURFACE,
        linewidths=0.8,
        label=labels[1],
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df.index, fontsize=8, color=INK_SECONDARY)
    ax.set_xscale("log")
    ticks = [1, 1.5, 2, 3, 5, 8, 12]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}x" for t in ticks])
    ax.set_xlabel("dynamical ceiling (true mass / minimum mass)", color=INK_SECONDARY)
    ax.set_title(
        "Longer clocks, tighter ceilings",
        color=INK,
        fontsize=12,
        loc="left",
        pad=12,
    )
    legend = ax.legend(loc="lower right", frameon=False, fontsize=8)
    for text in legend.get_texts():
        text.set_color(INK_SECONDARY)
    ax.set_ylim(-0.7, len(df) - 0.3)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def plot_floor_ceiling(catalog: pd.DataFrame, path: str) -> None:
    """Headline figure: RV mass floor vs dynamical ceiling, planet by planet.

    One dumbbell per swept planet with a finite ceiling: solid dot at msini,
    dark tick at the ceiling, a light span between — one quantity, one hue.
    """
    df = catalog[catalog["mass_ceiling_mjup"].notna() & catalog["swept"]].copy()
    df = df.sort_values("mass_ceiling_mjup").reset_index(drop=True)
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(7.5, 1.2 + 0.32 * len(df)), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)
    ax.grid(axis="y", visible=False)

    y = np.arange(len(df))
    ax.hlines(
        y,
        df["msini_mjup"],
        df["mass_ceiling_mjup"],
        color=BLUE_LIGHT,
        linewidth=2,
        zorder=2,
    )
    ax.scatter(
        df["msini_mjup"], y, s=28, color=SERIES_1, zorder=3, edgecolors=SURFACE, linewidths=0.8
    )
    ax.scatter(df["mass_ceiling_mjup"], y, s=90, color=BLUE_DARK, zorder=3, marker="|")

    ax.axvline(DEUTERIUM_LIMIT_MJUP, color=BASELINE, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    ax.annotate(
        "deuterium limit",
        xy=(DEUTERIUM_LIMIT_MJUP, len(df) - 0.4),
        xytext=(DEUTERIUM_LIMIT_MJUP * 1.1, len(df) - 0.4),
        color=MUTED,
        fontsize=8,
        va="center",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["planet"], fontsize=8, color=INK_SECONDARY)
    ax.set_xscale("log")
    ax.set_xlabel("mass (Jupiter masses)", color=INK_SECONDARY)
    ax.set_title(
        "Mass floor (msini, dot) vs dynamical ceiling (tick)",
        color=INK,
        fontsize=12,
        loc="left",
        pad=12,
    )
    ax.set_ylim(-0.7, len(df) - 0.3)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
