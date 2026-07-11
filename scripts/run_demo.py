"""End-to-end sweep of one RV system.

Usage: python scripts/run_demo.py [hostname] [t_max_yr]
           [--draws N] [--seed N] [--incs 90,40,30,...] [--tag suffix] [--workers N]

Defaults to HD 12661 over 1e4 yr. Writes runs CSV + survival figure to results/.
"""

import argparse

import numpy as np

from dynamass import critical_mass_factor, fetch_system, inclination_sweep, survival_curve
from dynamass.paths import results_dir, slug
from dynamass.plotting import plot_survival_curve
from dynamass.stability import system_seed
from dynamass.system import mass_factor_to_inclination_deg

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hostname", nargs="?", default="HD 12661")
    ap.add_argument("t_max_yr", nargs="?", type=float, default=1e4)
    ap.add_argument("--draws", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None, help="default: deterministic per-system seed")
    ap.add_argument("--incs", default=None, help="comma-separated inclinations in degrees")
    ap.add_argument("--tag", default="", help="suffix for output filenames")
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    system = fetch_system(args.hostname, allow_fallback=True)
    seed = system_seed(system.name) if args.seed is None else args.seed
    incs = np.array([float(x) for x in args.incs.split(",")]) if args.incs else None

    print(f"System: {system.name}")
    print(f"  star: {system.star_mass_msun:.2f} Msun")
    for p in system.sorted_planets():
        kind = "msini" if p.swept else ("transiting" if p.transiting else "true mass")
        print(f"  {p.name}: P = {p.period_days:.1f} d, m = {p.msini_mjup:.2f} Mjup ({kind}), e = {p.ecc:.2f}")

    print(f"\nSweeping coplanar inclination, t_max = {args.t_max_yr:,.0f} yr ...")
    runs = inclination_sweep(
        system,
        inclinations_deg=incs,
        n_draws=args.draws,
        t_max_yr=args.t_max_yr,
        seed=seed,
        workers=args.workers,
    )

    curve = survival_curve(runs)
    ceiling = critical_mass_factor(runs)

    out = results_dir()
    base = slug(system.name) + (f"_{args.tag}" if args.tag else "")
    runs.to_csv(out / f"{base}_runs.csv", index=False)
    plot_survival_curve(curve, system, args.t_max_yr, ceiling, str(out / f"{base}_survival.png"))

    print(f"\nRuns: {len(runs)}, survived: {int(runs['survived'].sum())}")
    if ceiling is None:
        print("No dynamical ceiling found in the swept range (all configurations survived).")
    else:
        inc = mass_factor_to_inclination_deg(ceiling)
        print(f"Dynamical ceiling: m < {ceiling:.2f} x msini  (i > {inc:.0f} deg)")
        for p in system.sorted_planets():
            if p.swept:
                print(
                    f"  {p.name}: msini = {p.msini_mjup:.2f} Mjup -> "
                    f"true mass < {p.true_mass_mjup(ceiling):.2f} Mjup"
                )
    print(f"\nWrote {out / (base + '_runs.csv')}")
    print(f"Wrote {out / (base + '_survival.png')}")


# The parallel sweep spawns workers that re-import this file; the guard keeps
# them from re-running the sweep themselves.
if __name__ == "__main__":
    main()
