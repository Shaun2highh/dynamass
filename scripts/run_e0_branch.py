"""Conservative e=0 branch for systems flagged unstable at edge-on.

The Barnard diagnostic showed catalog eccentricity point-estimates can be
fatal noise in compact systems. Re-sweep the flagged systems with circular
orbits: if a ceiling emerges, report it as the conservative-circular limit.
"""

from dynamass import fetch_system, inclination_sweep
from dynamass.paths import results_dir, slug
from dynamass.stability import summarize_system, system_seed

FLAGGED = ["Barnard's star", "HIP 57274", "Kepler-20"]
N_ORBITS = 1e6


def main() -> None:
    out_dir = results_dir("survey_1e6_e0")
    for host in FLAGGED:
        system = fetch_system(host)
        for p in system.planets:
            p.ecc = 0.0
        t_max_yr = N_ORBITS * system.min_period_yr
        print(f"\n{host}: e=0 sweep, t_max = {t_max_yr:,.0f} yr", flush=True)
        runs = inclination_sweep(
            system, n_draws=5, t_max_yr=t_max_yr, seed=system_seed(host), workers=8
        )
        runs.to_csv(out_dir / f"{slug(host)}_runs.csv", index=False)
        ceiling = summarize_system(system, runs)["ceiling_factor"]
        status = "no ceiling in range" if ceiling is None else f"m < {ceiling:.2f} x msini"
        print(f"{host}: e=0 ceiling = {status}", flush=True)


# The parallel sweep spawns workers that re-import this file; the guard keeps
# them from re-running the sweep themselves.
if __name__ == "__main__":
    main()
