"""Why does the published GJ 876 fit die in our pipeline?

Separates the two suspects:
  numerics — WHFast timestep too coarse for the eccentric resonance
             (test: shrink dt; switch to IAS15, an exact adaptive integrator);
  criterion — Hill-sphere overlap flags bounded resonant close approaches as
             instability (test: track the actual minimum pair separation in
             mutual Hill radii under IAS15 with collisions disabled).
"""

import math

import numpy as np
import rebound

from dynamass import fetch_system
from dynamass.integrate import DT_FRACTION, build_sim
from dynamass.system import mutual_hill_radius_au

I_FIT_DEG = 59.0
T_MAX_YR = 5e3


def make_system():
    system = fetch_system("GJ 876")
    sin_i = math.sin(math.radians(I_FIT_DEG))
    for p in system.planets:
        p.msini_mjup *= sin_i
        p.mass_is_msini = True
    return system, 1.0 / sin_i


def run_variant(label, dt_scale=1.0, integrator="whfast"):
    system, f_fit = make_system()
    rng = np.random.default_rng(1)
    sim = build_sim(system, f_fit, rng, sample_uncertainties=False)
    if integrator != "whfast":
        sim.integrator = integrator
    sim.dt *= dt_scale
    try:
        sim.integrate(T_MAX_YR, exact_finish_time=0)
        print(f"  {label}: survived to t = {sim.t:,.0f} yr", flush=True)
    except rebound.Collision:
        print(f"  {label}: close_encounter at t = {sim.t:,.0f} yr", flush=True)
    except rebound.Escape:
        print(f"  {label}: escape at t = {sim.t:,.0f} yr", flush=True)


def min_separations():
    """IAS15, collisions off: how close do pairs actually get (in mutual Hill radii)?"""
    system, f_fit = make_system()
    rng = np.random.default_rng(1)
    sim = build_sim(system, f_fit, rng, sample_uncertainties=False)
    sim.integrator = "ias15"
    sim.collision = "none"
    ps = sim.particles
    n = len(ps) - 1
    mstar = ps[0].m
    names = [p.name for p in system.sorted_planets()]
    a0 = [ps[i].a for i in range(1, n + 1)]
    m0 = [ps[i].m for i in range(1, n + 1)]
    min_rh = {(i, j): np.inf for i in range(n) for j in range(i + 1, n)}
    for t in np.linspace(0, T_MAX_YR, 20000):
        sim.integrate(t, exact_finish_time=0)
        for i in range(n):
            for j in range(i + 1, n):
                d = ps[i + 1] - ps[j + 1]
                dist = math.sqrt(d.x**2 + d.y**2 + d.z**2)
                rh = mutual_hill_radius_au(a0[i], a0[j], m0[i], m0[j], mstar)
                min_rh[(i, j)] = min(min_rh[(i, j)], dist / rh)
    print("\n  minimum pair separations over the run (mutual Hill radii):", flush=True)
    for (i, j), v in min_rh.items():
        print(f"    {names[i]} / {names[j]}: {v:.2f}", flush=True)


if __name__ == "__main__":
    print("Anchor variants (published fit, fixed phases):", flush=True)
    run_variant("whfast, dt nominal (baseline)")
    run_variant("whfast, dt/3", dt_scale=1 / 3)
    run_variant("ias15 (exact), Hill-overlap collisions", integrator="ias15")
    min_separations()
