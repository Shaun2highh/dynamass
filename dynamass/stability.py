"""Inclination sweep for one system: the survival grid and the mass ceiling."""

from __future__ import annotations

import math
import zlib
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from .integrate import run_one
from .system import System, inclination_deg_to_mass_factor, mass_factor_to_inclination_deg

DEFAULT_INCLINATIONS = np.array(
    [90, 70, 55, 45, 38, 32, 27, 23, 19, 16, 13.5, 11.5, 10, 8.5, 7, 6, 5], dtype=float
)


def system_seed(name: str) -> int:
    """Deterministic per-system seed, shared by every runner and diagnostic."""
    return zlib.crc32(name.encode()) % 100_000


def inclination_sweep(
    system: System,
    inclinations_deg: np.ndarray | None = None,
    n_draws: int = 5,
    t_max_yr: float = 1e4,
    seed: int = 0,
    verbose: bool = True,
    workers: int = 1,
) -> pd.DataFrame:
    """Integrate n_draws phase realizations at each line-of-sight inclination.

    Returns one row per run: inclination, mass_factor, draw, survived,
    t_end_yr, reason. The (inclination, draw) grid is embarrassingly parallel;
    pass workers > 1 to fan it out over processes.
    """
    if inclinations_deg is None:
        inclinations_deg = DEFAULT_INCLINATIONS

    specs = [
        (inc, inclination_deg_to_mass_factor(inc), draw, seed * 100_000 + int(inc * 100) + draw)
        for inc in inclinations_deg
        for draw in range(n_draws)
    ]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(
                pool.map(
                    run_one,
                    (system for _ in specs),
                    (factor for _, factor, _, _ in specs),
                    (t_max_yr for _ in specs),
                    (run_seed for *_, run_seed in specs),
                )
            )
    else:
        results = [
            run_one(system, factor, t_max_yr, seed=run_seed) for _, factor, _, run_seed in specs
        ]

    rows = [
        dict(
            system=system.name,
            inclination_deg=inc,
            mass_factor=factor,
            draw=draw,
            survived=res.survived,
            t_end_yr=res.t_end_yr,
            reason=res.reason,
        )
        for (inc, factor, draw, _), res in zip(specs, results)
    ]
    if verbose:
        for start in range(0, len(rows), n_draws):
            chunk = rows[start : start + n_draws]
            frac = np.mean([r["survived"] for r in chunk])
            print(
                f"  i = {chunk[0]['inclination_deg']:5.1f} deg  "
                f"(m = {chunk[0]['mass_factor']:5.2f} x msini)  survival = {frac:.0%}"
            )
    return pd.DataFrame(rows)


def survival_curve(runs: pd.DataFrame) -> pd.DataFrame:
    """Survival fraction per inclination, sorted from edge-on to face-on."""
    grouped = (
        runs.groupby(["inclination_deg", "mass_factor"])["survived"]
        .mean()
        .reset_index()
        .rename(columns={"survived": "survival_fraction"})
        .sort_values("inclination_deg", ascending=False)
    )
    return grouped


def edge_on_survival(runs: pd.DataFrame) -> float:
    """Survival fraction at the smallest swept mass factor (edge-on baseline)."""
    curve = survival_curve(runs).sort_values("mass_factor")
    return float(curve["survival_fraction"].iloc[0])


def critical_mass_factor(runs: pd.DataFrame, threshold: float = 0.5) -> float | None:
    """Smallest swept mass factor whose survival drops below threshold *relative
    to the edge-on baseline*.

    The relative criterion separates the two things a low survival fraction can
    mean: parameter draws that are fragile at any tilt (baseline already low —
    a consistency flag, not a mass limit) versus configurations killed by the
    extra mass itself (survival degrading with the factor — the ceiling).
    None if nothing degrades below threshold * baseline in the swept range.
    """
    curve = survival_curve(runs).sort_values("mass_factor")
    baseline = float(curve["survival_fraction"].iloc[0])
    if baseline <= 0.0:
        return float(curve["mass_factor"].iloc[0])
    unstable = curve[curve["survival_fraction"] < threshold * baseline]
    if unstable.empty:
        return None
    return float(unstable["mass_factor"].iloc[0])


def credible_mass_limit(runs: pd.DataFrame, cred: float = 0.95) -> float | None:
    """Upper limit on the mass factor at credibility `cred` under an isotropic
    orientation prior (uniform in cos i).

    The posterior density over cos i is proportional to the survival
    probability at that inclination; the limit is the mass factor where the
    posterior CDF (accumulated from edge-on toward face-on) reaches `cred`.
    Survival outside the sampled inclination range is extrapolated flat.
    None if nothing survives anywhere (a hard parameter-consistency flag).
    """
    curve = survival_curve(runs)
    cos_sampled = np.cos(np.radians(curve["inclination_deg"].to_numpy()))
    surv = curve["survival_fraction"].to_numpy()
    order = np.argsort(cos_sampled)
    cos_grid = np.linspace(0.0, 1.0, 2001)
    s = np.interp(cos_grid, cos_sampled[order], surv[order])
    if s.sum() <= 0:
        return None
    cdf = np.cumsum(s) / s.sum()
    k = int(np.searchsorted(cdf, cred))
    cos_star = cos_grid[min(k, len(cos_grid) - 1)]
    sin_star = math.sqrt(max(1.0 - cos_star**2, 1e-6))
    return 1.0 / sin_star


def summarize_system(system: System, runs: pd.DataFrame) -> dict:
    """Per-system survey summary: the ceiling plus per-planet catalog rows.

    edge_on_survival < 0.5 marks a parameter-consistency flag: the catalog
    parameters are fragile regardless of tilt, so the ceiling (if any) should
    be read with that caveat.
    """
    ceiling = critical_mass_factor(runs)
    m95 = credible_mass_limit(runs)
    return dict(
        system=system.name,
        t_max_yr=float(runs["t_end_yr"].max()),
        n_runs=len(runs),
        edge_on_survival=edge_on_survival(runs),
        ceiling_factor=ceiling,
        m95_factor=m95,
        inc_floor_deg=None if ceiling is None else mass_factor_to_inclination_deg(ceiling),
        planets=[
            dict(
                planet=p.name,
                msini_mjup=p.msini_mjup,
                swept=p.swept,
                mass_ceiling_mjup=(
                    p.msini_mjup * ceiling if (ceiling is not None and p.swept) else None
                ),
                mass_95_mjup=(p.msini_mjup * m95 if (m95 is not None and p.swept) else None),
            )
            for p in system.sorted_planets()
        ],
    )
