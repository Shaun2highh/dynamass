"""N-body integration of one configuration until instability or t_max.

Coplanar convention: tilting a coplanar system relative to the line of sight
changes only the inferred masses, not the internal dynamics. So the sweep
scales every Msini mass by 1/sin(i) and integrates a coplanar system.
Mutual-inclination sweeps are a later extension.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import rebound

from .system import MSUN_PER_MJUP, System, hill_radius_au

# A close encounter inside the sum of Hill radii is treated as an instability:
# particles carry their Hill radius as a collision radius.
ESCAPE_FACTOR = 20.0  # exit_max_distance in units of the widest semi-major axis
DT_FRACTION = 1.0 / 20.0  # timestep as a fraction of the innermost perihelion period


@dataclass
class RunResult:
    survived: bool
    t_end_yr: float
    reason: str  # "survived" | "close_encounter" | "escape"


def _draw(
    rng: np.random.Generator,
    value: float,
    err: float,
    lo: float = -np.inf,
    hi: float = np.inf,
) -> float:
    """One draw from N(value, err) truncated to [lo, hi].

    Falls back to the (clipped) point value when the error is unreported.
    """
    if not (np.isfinite(err) and err > 0):
        return float(np.clip(value, lo, hi))
    for _ in range(64):
        x = rng.normal(value, err)
        if lo <= x <= hi:
            return float(x)
    return float(np.clip(value, lo, hi))


def build_sim(
    system: System,
    mass_factor: float,
    rng: np.random.Generator,
    sample_uncertainties: bool = True,
) -> rebound.Simulation:
    sim = rebound.Simulation()
    sim.units = ("yr", "AU", "Msun")
    mstar = (
        _draw(rng, system.star_mass_msun, system.star_mass_err_msun, lo=0.05)
        if sample_uncertainties
        else system.star_mass_msun
    )
    sim.add(m=mstar)

    dt_min = np.inf
    for p in system.sorted_planets():
        if sample_uncertainties:
            msini = _draw(rng, p.msini_mjup, p.msini_err_mjup, lo=1e-8)
            period_yr = _draw(rng, p.period_days, p.period_err_days, lo=1e-6) / 365.25
            ecc = _draw(rng, p.ecc, p.ecc_err, lo=0.0, hi=0.95)
        else:
            msini, period_yr, ecc = p.msini_mjup, p.period_yr, min(p.ecc, 0.95)
        m = msini * (mass_factor if p.swept else 1.0) * MSUN_PER_MJUP
        if np.isfinite(p.lper_deg):
            lper = _draw(rng, p.lper_deg, p.lper_err_deg) if sample_uncertainties else p.lper_deg
            omega = np.radians(lper)
        else:
            omega = rng.uniform(0.0, 2.0 * np.pi)
        # Phases from the fit (via time of periastron) when known — essential
        # for resonance-protected systems — else drawn uniformly.
        if np.isfinite(p.mean_anom_deg):
            mean_anom = np.radians(p.mean_anom_deg)
        else:
            mean_anom = rng.uniform(0.0, 2.0 * np.pi)
        sim.add(m=m, P=period_yr, e=ecc, omega=omega, M=mean_anom)
        part = sim.particles[-1]
        part.r = hill_radius_au(part.a, m, mstar)
        dt_min = min(dt_min, period_yr * (1.0 - ecc) ** 1.5)

    sim.move_to_com()
    sim.integrator = "whfast"
    # Resolve the fastest perihelion passage among the planets.
    sim.dt = dt_min * DT_FRACTION
    sim.collision = "direct"
    sim.collision_resolve = "halt"
    sim.exit_max_distance = ESCAPE_FACTOR * max(pt.a for pt in sim.particles[1:])
    return sim


def run_one(
    system: System,
    mass_factor: float,
    t_max_yr: float,
    seed: int,
    sample_uncertainties: bool = True,
) -> RunResult:
    rng = np.random.default_rng(seed)
    sim = build_sim(system, mass_factor, rng, sample_uncertainties=sample_uncertainties)
    try:
        sim.integrate(t_max_yr, exact_finish_time=0)
    except rebound.Collision:
        return RunResult(False, sim.t, "close_encounter")
    except rebound.Escape:
        return RunResult(False, sim.t, "escape")
    return RunResult(True, sim.t, "survived")
