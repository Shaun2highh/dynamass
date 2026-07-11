"""Second validation anchor: HD 45364 (two giants in 3:2 resonance,
Correia et al. 2009).

Unlike GJ 876 the published fit is already an msini solution, so edge-on is
the fit itself. Checks: (1) the fit with its own phases survives; (2) phase
scrambling degrades survival (resonance protection); (3) the sweep yields a
finite ceiling. Falls back with a clear message if no single-reference
parameter set with phases exists in the archive.
"""

import copy

from dynamass import critical_mass_factor, inclination_sweep
from dynamass.integrate import run_one
from dynamass.paths import results_dir, slug
from dynamass.plotting import plot_survival_curve
from dynamass.stability import credible_mass_limit, survival_curve, system_seed
from dynamass.system import mass_factor_to_inclination_deg
from dynamass.targets import fetch_system_single_ref

HOST = "HD 45364"
T_MAX_YR = 1e5


def main() -> None:
    system = fetch_system_single_ref(HOST)
    print(f"Parameter source: {system.ref}")
    for p in system.sorted_planets():
        print(
            f"  {p.name}: P = {p.period_days:.2f} d, msini = {p.msini_mjup:.3f} Mjup, "
            f"e = {p.ecc:.3f}, M0 = {p.mean_anom_deg:.1f} deg"
        )
    if any(not (p.mean_anom_deg == p.mean_anom_deg) for p in system.planets):
        print("No usable phases in the archive for this reference — anchor limited to sweep only.")

    anchor = run_one(system, 1.0, T_MAX_YR, seed=1, sample_uncertainties=False)
    print(f"\nAnchor (published fit, fixed phases): {anchor.reason} at t = {anchor.t_end_yr:,.0f} yr")

    rand = copy.deepcopy(system)
    for p in rand.planets:
        p.mean_anom_deg = float("nan")
    rand_res = [
        run_one(rand, 1.0, T_MAX_YR, seed=100 + i, sample_uncertainties=False) for i in range(8)
    ]
    frac = sum(r.survived for r in rand_res) / len(rand_res)
    print(f"Same masses with RANDOM phases: survival {frac:.0%} (resonance protection check)")

    print(f"\nSweeping with fixed phases, t_max = {T_MAX_YR:,.0f} yr ...")
    runs = inclination_sweep(
        system, n_draws=10, t_max_yr=T_MAX_YR, seed=system_seed(HOST), workers=8
    )
    ceiling = critical_mass_factor(runs)
    m95 = credible_mass_limit(runs)
    out = results_dir()
    runs.to_csv(out / f"{slug(HOST)}_validation_runs.csv", index=False)
    plot_survival_curve(
        survival_curve(runs), system, T_MAX_YR, ceiling,
        str(out / f"{slug(HOST)}_validation.png"),
    )
    if ceiling is None:
        print("No threshold ceiling in the swept range.")
    else:
        print(f"Threshold ceiling: m < {ceiling:.2f} x msini (i > {mass_factor_to_inclination_deg(ceiling):.0f} deg)")
    print(f"95% credible limit: {'none' if m95 is None else f'm < {m95:.2f} x msini'}")


# Guard required: the parallel sweep's spawn workers re-import this file.
if __name__ == "__main__":
    main()
