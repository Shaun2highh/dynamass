"""Sensitivity analysis on a representative subset: does the 95% credible
mass limit move under (a) half the timestep, (b) smaller collision radii,
(c) modest mutual inclinations? A limit that shifts less than a grid step
under all variants supports the survey's numerical choices.

Usage: python scripts/sensitivity.py  (writes results/sensitivity.csv)
"""

import os

import pandas as pd

from dynamass import fetch_system, inclination_sweep
from dynamass.paths import results_dir
from dynamass.stability import credible_mass_limit, edge_on_survival, system_seed

SYSTEMS = ["Barnard's star", "K2-18", "YZ Cet", "HD 147873", "HIP 111909", "HD 50499"]
VARIANTS = {
    "baseline": {},
    "dt_half": {"dt_scale": 0.5},
    "rcoll_050": {"collision_r_scale": 0.5},
    "rcoll_025": {"collision_r_scale": 0.25},
    "mutinc_2deg": {"mutual_inc_sigma_deg": 2.0},
    "mutinc_5deg": {"mutual_inc_sigma_deg": 5.0},
}
N_ORBITS = 1e5
N_DRAWS = 10


def main() -> None:
    rows = []
    workers = os.cpu_count() or 4
    for hostname in SYSTEMS:
        system = fetch_system(hostname)
        t_max_yr = N_ORBITS * system.min_period_yr
        for variant, kwargs in VARIANTS.items():
            runs = inclination_sweep(
                system,
                n_draws=N_DRAWS,
                t_max_yr=t_max_yr,
                seed=system_seed(hostname),
                verbose=False,
                workers=workers,
                run_kwargs=kwargs or None,
            )
            rows.append(
                dict(
                    system=hostname,
                    variant=variant,
                    edge_on_survival=edge_on_survival(runs),
                    m95_factor=credible_mass_limit(runs),
                )
            )
            r = rows[-1]
            m95 = "none" if r["m95_factor"] is None else f"{r['m95_factor']:.2f}"
            print(
                f"  {hostname} / {variant}: edge-on {r['edge_on_survival']:.0%}, m95 {m95}",
                flush=True,
            )
    df = pd.DataFrame(rows)
    out = results_dir() / "sensitivity.csv"
    df.to_csv(out, index=False)
    pivot = df.pivot(index="system", columns="variant", values="m95_factor").round(2)
    print("\n95% credible mass factor by variant:", flush=True)
    print(pivot.to_string(), flush=True)
    print(f"\nWrote {out}", flush=True)


# Guard required: the parallel sweep's spawn workers re-import this file.
if __name__ == "__main__":
    main()
