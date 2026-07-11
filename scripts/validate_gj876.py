"""Pipeline validation against GJ 876, the classic stability-constrained system.

The archive's default GJ 876 solution is a coplanar dynamical fit at i = 59
deg (true masses, resonant phases at the libration center). We reconstruct
the msini system (msini = m_true * sin 59), keep the fit's phases fixed, and
sweep inclination. Checks:
  1. anchor: the published configuration (factor = 1/sin 59) must survive;
  2. the ceiling should approach the literature constraint (i > ~20 deg);
  3. with randomized phases the nominal system should NOT reliably survive
     (resonance protection matters), justifying the phase-constrained init.
"""

import copy
import math

import numpy as np

from dynamass import critical_mass_factor, inclination_sweep
from dynamass.integrate import run_one
from dynamass.paths import results_dir, slug
from dynamass.plotting import plot_survival_curve
from dynamass.stability import survival_curve, system_seed
from dynamass.targets import fetch_system_single_ref
from dynamass.system import mass_factor_to_inclination_deg

I_FIT_DEG = 59.0
T_MAX_YR = 5e3
INCS = np.array([90, 59, 40, 30, 25, 20, 17, 14, 12, 10, 8, 6, 5], dtype=float)


# Mean anomalies at epoch JD 2450602.093 from Rivera et al. 2010, Table 3
# (i = 59 deg coplanar fit). The archive's pl_orbtper holds the epoch itself
# for this reference, so phases cannot be derived from it.
RIVERA2010_MEAN_ANOM_DEG = {"d": 355.0, "c": 294.59, "b": 325.7, "e": 335.0}


def main() -> None:
    # Single self-consistent fit — pscomppars composites break resonant phases.
    system = fetch_system_single_ref("GJ 876")
    print(f"Parameter source: {system.ref}")
    for p in system.planets:
        p.mean_anom_deg = RIVERA2010_MEAN_ANOM_DEG[p.name.split()[-1]]
    sin_i = math.sin(math.radians(I_FIT_DEG))
    for p in system.planets:
        p.msini_mjup *= sin_i
        p.msini_err_mjup *= sin_i
        p.mass_is_msini = True

    f_fit = 1.0 / sin_i
    print(f"GJ 876 reconstructed msini system (fit at factor {f_fit:.3f}):")
    for p in system.sorted_planets():
        print(f"  {p.name}: P = {p.period_days:.4f} d, msini = {p.msini_mjup:.4f} Mjup, "
              f"e = {p.ecc:.4f}, M0 = {p.mean_anom_deg:.1f} deg")

    anchor = run_one(system, f_fit, T_MAX_YR, seed=1, sample_uncertainties=False)
    print(f"\nAnchor (published fit, fixed phases): {anchor.reason} at t = {anchor.t_end_yr:,.0f} yr")

    rand = copy.deepcopy(system)
    for p in rand.planets:
        p.mean_anom_deg = float("nan")
    rand_res = [run_one(rand, f_fit, T_MAX_YR, seed=100 + i, sample_uncertainties=False) for i in range(8)]
    frac = sum(r.survived for r in rand_res) / len(rand_res)
    print(f"Same masses with RANDOM phases: survival {frac:.0%} (resonance protection check)")

    print(f"\nSweeping with fixed phases, t_max = {T_MAX_YR:,.0f} yr ...")
    runs = inclination_sweep(
        system, inclinations_deg=INCS, n_draws=5, t_max_yr=T_MAX_YR,
        seed=system_seed(system.name), workers=8,
    )
    ceiling = critical_mass_factor(runs)
    out = results_dir()
    runs.to_csv(out / f"{slug(system.name)}_validation_runs.csv", index=False)
    plot_survival_curve(
        survival_curve(runs), system, T_MAX_YR, ceiling,
        str(out / f"{slug(system.name)}_validation.png"),
    )
    if ceiling is None:
        print("No ceiling in range — validation FAILED (literature expects one).")
    else:
        inc = mass_factor_to_inclination_deg(ceiling)
        print(f"Ceiling: m < {ceiling:.2f} x msini  (i > {inc:.0f} deg); literature: i > ~20 deg")


# Guard required: the parallel sweep's spawn workers re-import this file.
if __name__ == "__main__":
    main()
