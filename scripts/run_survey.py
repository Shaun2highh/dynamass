"""v0 survey pass: inclination sweeps across the ranked target list.

Uniform effort per system: t_max = n_inner_orbits inner-planet orbits, 11
inclinations, 5 phase draws. Systems run in parallel processes; finished
systems are skipped on restart (resumable). Writes per-system run CSVs to
results/survey{tag}/, then a per-planet catalog and the headline
floor-vs-ceiling figure.

Usage: python scripts/run_survey.py [max_systems] [n_inner_orbits] [label] [n_draws]

The optional label (e.g. "v1") keeps runs with different sampling semantics in
separate cache directories and catalogs — v0 caches used catalog point
estimates; runs since 2026-07-11 sample parameters within uncertainties.
"""

import os
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from dynamass import fetch_qualifying_systems, fetch_system, inclination_sweep
from dynamass.paths import depth_tag, results_dir, slug
from dynamass.stability import summarize_system, system_seed
from dynamass.system import System

# v0 exclusions, documented in README: the f_crit ~ 1 block is dominated by
# resonance-protected systems that random phases would falsely destabilize.
F_CRIT_MIN = 1.05
F_CRIT_MAX = 60.0
MAX_ECC = 0.75
MIN_PERIOD_D = 1.5


def survey_one(system: System, n_orbits: float, survey_dir: str, n_draws: int) -> dict:
    t_max_yr = n_orbits * system.min_period_yr
    runs = inclination_sweep(
        system, n_draws=n_draws, t_max_yr=t_max_yr, seed=system_seed(system.name), verbose=False
    )
    runs.to_csv(pathlib.Path(survey_dir) / f"{slug(system.name)}_runs.csv", index=False)
    return summarize_system(system, runs)


def main() -> None:
    max_systems = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    n_orbits = float(sys.argv[2]) if len(sys.argv) > 2 else 1e5
    tag = depth_tag(n_orbits)
    if len(sys.argv) > 3:
        tag += f"_{sys.argv[3]}"
    n_draws = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    survey_dir = results_dir(f"survey{tag}")
    print(f"Depth: {n_orbits:g} inner orbits -> {survey_dir}", flush=True)

    targets = pd.read_csv(results_dir() / "targets.csv")
    band = targets[
        (targets.f_crit >= F_CRIT_MIN)
        & (targets.f_crit <= F_CRIT_MAX)
        & (targets.max_ecc <= MAX_ECC)
        & (targets.min_period_d >= MIN_PERIOD_D)
    ].sort_values("f_crit")
    band = band.head(max_systems)
    print(f"{len(band)} systems in the v0 band", flush=True)

    # One bulk archive query up front; the workers then do zero network I/O.
    systems = {s.name: s for s in fetch_qualifying_systems()}

    summaries, todo = [], []
    for hostname in band.system:
        system = systems.get(hostname) or fetch_system(hostname)
        done_csv = survey_dir / f"{slug(hostname)}_runs.csv"
        if done_csv.exists():
            summaries.append(summarize_system(system, pd.read_csv(done_csv)))
            print(f"  [cached]  {hostname}", flush=True)
        else:
            todo.append(system)

    with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        futures = {pool.submit(survey_one, s, n_orbits, str(survey_dir), n_draws): s.name for s in todo}
        for fut in as_completed(futures):
            hostname = futures[fut]
            try:
                summary = fut.result()
            except Exception as exc:
                print(f"  [failed]  {hostname}: {exc}", flush=True)
                continue
            summaries.append(summary)
            c = summary["ceiling_factor"]
            status = "no ceiling in range" if c is None else f"m < {c:.2f} x msini"
            print(f"  [done]    {hostname}: {status}", flush=True)

    rows = [
        dict(
            system=s["system"],
            planet=p["planet"],
            msini_mjup=p["msini_mjup"],
            swept=p["swept"],
            edge_on_survival=s["edge_on_survival"],
            ceiling_factor=s["ceiling_factor"],
            m95_factor=s["m95_factor"],
            mass_ceiling_mjup=p["mass_ceiling_mjup"],
            mass_95_mjup=p["mass_95_mjup"],
            inc_floor_deg=s["inc_floor_deg"],
            t_max_yr=s["t_max_yr"],
        )
        for s in summaries
        for p in s["planets"]
    ]
    catalog = pd.DataFrame(rows)
    catalog.to_csv(results_dir() / f"survey_catalog{tag}.csv", index=False)

    n_ceiling = int(catalog.mass_ceiling_mjup.notna().sum())
    print(f"\nCatalog: {len(catalog)} planets in {len(summaries)} systems", flush=True)
    print(f"Planets with a dynamical ceiling: {n_ceiling}", flush=True)

    # Deferred import: spawn workers re-import this module and shouldn't pay
    # for matplotlib.
    from dynamass.plotting import plot_floor_ceiling

    plot_floor_ceiling(catalog, str(results_dir() / f"floor_vs_ceiling{tag}.png"))
    print(f"Wrote results/survey_catalog{tag}.csv and results/floor_vs_ceiling{tag}.png", flush=True)


if __name__ == "__main__":
    main()
