"""The non-coplanar dimension: the 95% credible mass limit as a function of
assumed mutual-inclination dispersion.

The main survey tilts each system as a rigid coplanar body, so the reported
limits are conditional on approximate coplanarity. The sensitivity analysis
(scripts/sensitivity.py) already showed the limits move by <=0.4 in the mass
factor for mutual-inclination dispersions of 2-5 deg on six systems. Here we
extend that into a full axis: for an architecture-spanning subset we sweep the
mutual-inclination dispersion sigma from 0 (coplanar) to 30 deg, drawing each
planet's mutual inclination from a Rayleigh(sigma) distribution and its node
uniformly, on top of the usual line-of-sight inclination sweep. The output is
the limit m95(sigma) per system: how much the constraint weakens, and where
non-coplanarity alone begins to destabilize the published configuration.

Usage: python scripts/run_mutual_inc.py [n_orbits] [n_draws] [workers]
Writes results/mutual_inc.csv and results/mutual_inc.png.
"""

import os
import sys

import pandas as pd

from dynamass import fetch_system, inclination_sweep
from dynamass.paths import results_dir
from dynamass.stability import credible_mass_limit, edge_on_survival, system_seed

# Architecture-spanning subset: compact sub-Earth systems, giants, and mixed.
SYSTEMS = [
    "Barnard's star", "YZ Cet", "L 98-59",          # compact sub-Earths
    "K2-18", "HD 147873", "HIP 111909",             # mixed / mid-mass
    "47 UMa", "HD 141399", "HD 50499", "HD 95089",  # giants
]
SIGMAS_DEG = [0.0, 5.0, 10.0, 15.0, 20.0, 30.0]     # mutual-inclination dispersion


def main() -> None:
    n_orbits = float(sys.argv[1]) if len(sys.argv) > 1 else 1e5
    n_draws = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    # Default to 2 workers so this can coexist with another survey run.
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    print(f"Non-coplanar sweep: {len(SYSTEMS)} systems x {len(SIGMAS_DEG)} sigmas, "
          f"{n_orbits:g} orbits, {n_draws} draws, {workers} workers", flush=True)

    rows = []
    for hostname in SYSTEMS:
        system = fetch_system(hostname)
        t_max_yr = n_orbits * system.min_period_yr
        for sigma in SIGMAS_DEG:
            kwargs = {"mutual_inc_sigma_deg": sigma} if sigma > 0 else None
            runs = inclination_sweep(
                system, n_draws=n_draws, t_max_yr=t_max_yr,
                seed=system_seed(hostname), verbose=False, workers=workers,
                run_kwargs=kwargs,
            )
            m95 = credible_mass_limit(runs)
            s90 = edge_on_survival(runs)
            rows.append(dict(system=hostname, sigma_deg=sigma,
                             edge_on_survival=s90, m95_factor=m95))
            m = "none" if m95 is None else f"{m95:.2f}"
            print(f"  {hostname:16s} sigma={sigma:4.0f}  S(90)={s90:.2f}  m95={m}",
                  flush=True)

    df = pd.DataFrame(rows)
    out = results_dir() / "mutual_inc.csv"
    df.to_csv(out, index=False)
    pivot = df.pivot(index="system", columns="sigma_deg", values="m95_factor").round(2)
    print("\nm95 factor vs mutual-inclination dispersion (deg):", flush=True)
    print(pivot.to_string(), flush=True)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        for host, g in df.groupby("system"):
            g = g.sort_values("sigma_deg")
            ax.plot(g["sigma_deg"], g["m95_factor"], marker="o", label=host)
        ax.axhline(3.20, ls="--", color="0.5", lw=1,
                   label="isotropic bound (3.20)")
        ax.set_xlabel(r"mutual-inclination dispersion $\sigma$ (deg)")
        ax.set_ylabel(r"95% credible mass factor $m_{95}/m\sin i$")
        ax.set_title("Mass limit vs non-coplanarity")
        ax.legend(fontsize=7, ncol=2)
        fig.tight_layout()
        fig.savefig(results_dir() / "mutual_inc.png", dpi=150)
        print(f"Wrote {results_dir() / 'mutual_inc.png'}", flush=True)
    except Exception as exc:
        print(f"(plot skipped: {exc})", flush=True)

    print(f"Wrote {out}", flush=True)


if __name__ == "__main__":
    main()
