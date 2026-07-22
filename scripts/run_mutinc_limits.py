"""Mutual-inclination upper limits: the survey's second catalogue product.

The mass survey asks how heavy a system's planets can be before it destroys
itself. This asks the complementary architectural question: how *non-coplanar*
can the system be and still survive? We hold every planet at its minimum mass
(mass factor 1.0, i.e. the edge-on floor) so the constraint is purely
architectural and not entangled with the 1/sin i mass scaling, then raise the
mutual-inclination dispersion sigma. Each planet's inclination is drawn from a
Rayleigh(sigma) distribution with a uniform node, as in the sensitivity tests.

sigma_max is the smallest dispersion at which survival falls below half its
coplanar baseline -- the same relative criterion the mass survey uses for its
threshold ceiling, so the two catalogues are defined consistently.

Prior work: Volpi et al. (2019) bounded mutual inclinations for ten RV systems
with first-order secular theory. This is the homogeneous N-body version.

Usage: python scripts/run_mutinc_limits.py [n_orbits] [n_draws] [max_systems]
Writes results/mutinc_limits.csv and results/mutinc_limits.png.
"""

import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from dynamass import fetch_qualifying_systems
from dynamass.integrate import run_one
from dynamass.paths import results_dir
from dynamass.stability import system_seed

SIGMAS_DEG = [0.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0]
THRESHOLD = 0.5  # survival must stay above 0.5 x the coplanar baseline


def run_cell(system, sigma, n_draws, n_orbits, seed0):
    """Survival fraction for one (system, sigma) cell at the edge-on masses."""
    t_max_yr = n_orbits * system.min_period_yr
    survived = 0
    for d in range(n_draws):
        res = run_one(system, 1.0, t_max_yr, seed0 + int(sigma * 100) + d,
                      mutual_inc_sigma_deg=sigma)
        survived += bool(res.survived)
    return system.name, sigma, survived / n_draws


def sigma_limit(curve: dict) -> float | None:
    """Smallest sigma whose survival drops below THRESHOLD x the sigma=0 value."""
    base = curve.get(0.0, 0.0)
    if base <= 0:
        return None  # already fragile when coplanar: a consistency flag, not a limit
    for s in sorted(curve):
        if s > 0 and curve[s] < THRESHOLD * base:
            return s
    return None  # survives the whole sampled range


def main() -> None:
    n_orbits = float(sys.argv[1]) if len(sys.argv) > 1 else 1e5
    n_draws = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    max_systems = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    # The surveyed, unflagged systems: those with a real mass limit.
    cat = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")
    edge = cat.groupby("system")["edge_on_survival"].first()
    keep = set(edge[edge >= 0.5].index)
    systems = [s for s in fetch_qualifying_systems() if s.name in keep][:max_systems]
    print(f"Mutual-inclination limits: {len(systems)} systems x {len(SIGMAS_DEG)} sigmas, "
          f"{n_orbits:g} orbits, {n_draws} draws", flush=True)

    tasks = [(s, sig) for s in systems for sig in SIGMAS_DEG]
    curves: dict[str, dict[float, float]] = {s.name: {} for s in systems}
    workers = max(1, (os.cpu_count() or 4) - 2)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(run_cell, s, sig, n_draws, n_orbits,
                            system_seed(s.name) * 1000): (s.name, sig)
                for s, sig in tasks}
        done = 0
        for f in as_completed(futs):
            try:
                name, sig, frac = f.result()
            except Exception as exc:
                print(f"  [failed] {futs[f]}: {str(exc)[:50]}", flush=True)
                continue
            curves[name][sig] = frac
            done += 1
            if done % 25 == 0:
                print(f"  ... {done}/{len(tasks)} cells", flush=True)

    rows = []
    for name, curve in curves.items():
        lim = sigma_limit(curve)
        rows.append(dict(system=name, sigma_max_deg=lim,
                         baseline_survival=curve.get(0.0),
                         **{f"S_{int(s)}": curve.get(s) for s in SIGMAS_DEG}))
    df = pd.DataFrame(rows).sort_values("sigma_max_deg", na_position="last")
    out = results_dir() / "mutinc_limits.csv"
    df.to_csv(out, index=False)

    constrained = df[df.sigma_max_deg.notna()]
    print(f"\n{len(constrained)} of {len(df)} systems have a mutual-inclination limit")
    if len(constrained):
        print(f"median sigma_max = {constrained.sigma_max_deg.median():.0f} deg")
        print(constrained[["system", "sigma_max_deg"]].head(20).to_string(index=False))

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4.5))
        vals = constrained.sigma_max_deg.to_numpy()
        ax.hist(vals, bins=np.arange(0, 45, 5), edgecolor="k", alpha=.8)
        ax.set_xlabel(r"mutual-inclination limit $\sigma_{\max}$ (deg)")
        ax.set_ylabel("systems")
        ax.set_title("Stability-derived mutual-inclination limits")
        fig.tight_layout(); fig.savefig(results_dir() / "mutinc_limits.png", dpi=150)
        print(f"Wrote {results_dir()/'mutinc_limits.png'}")
    except Exception as exc:
        print(f"(plot skipped: {exc})")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
