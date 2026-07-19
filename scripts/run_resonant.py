"""Resonance-protected block: the survey's second half.

The main survey (scripts/run_survey.py) excludes systems with f_crit ~ 1,
which are dominated by resonant and near-resonant pairs. Randomized phases
falsely destabilize these systems, so they cannot be treated with composite
catalog parameters. Here we run them with the phase-coherent machinery
validated on GJ 876 (scripts/validate_gj876.py): each system is pulled from a
single self-consistent reference in the `ps` table, the orbital phases are
derived from that fit's time of periastron, and the inclination sweep holds
those phases fixed while sampling the remaining parameters within their
published uncertainties.

Systems without a complete single reference, or whose reference stores a fit
epoch in the periastron column (pitfall 3), cannot be phased and are recorded
as such rather than assigned a spurious limit.

Usage: python scripts/run_resonant.py [n_orbits] [n_draws] [max_systems]

Writes results/resonant{tag}/<system>_runs.csv (resumable), a per-planet
catalog results/resonant_catalog{tag}.csv, and a per-system status table
results/resonant_status{tag}.csv.
"""

import math
import os
import sys
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from dynamass import inclination_sweep
from dynamass.paths import depth_tag, results_dir, slug
from dynamass.stability import summarize_system, system_seed
from dynamass.targets import fetch_system_single_ref
from dynamass.system import System

# Finer inclination grid near edge-on than the default survey grid: resonant
# systems with f_crit ~ 1 can break close to 90 deg, where the default grid is
# coarse. Dense from 90 to 40 deg, then the standard tail.
INCLINATIONS = np.array(
    [90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 34, 28, 23, 19, 16, 13, 10, 8, 6, 5],
    dtype=float,
)


def phases_derived(system: System) -> bool:
    """True if at least one planet carries a fit-derived mean anomaly."""
    return any(math.isfinite(p.mean_anom_deg) for p in system.planets)


def survey_one(system: System, n_orbits: float, survey_dir: str, n_draws: int) -> dict:
    t_max_yr = n_orbits * system.min_period_yr
    runs = inclination_sweep(
        system,
        inclinations_deg=INCLINATIONS,
        n_draws=n_draws,
        t_max_yr=t_max_yr,
        seed=system_seed(system.name),
        verbose=False,
    )
    runs.to_csv(os.path.join(survey_dir, f"{slug(system.name)}_runs.csv"), index=False)
    summary = summarize_system(system, runs)
    summary["ref"] = getattr(system, "ref", "")
    summary["phased"] = phases_derived(system)
    return summary


def resonant_targets(max_systems: int) -> list[str]:
    t = pd.read_csv(results_dir() / "targets.csv")
    disp = pd.read_csv(pathlib_join("paper", "table1_dispositions.csv"))
    reso = disp[
        (disp.disposition == "excluded")
        & disp.reason.str.contains("resonance", case=False, na=False)
    ]
    return sorted(reso.system.tolist())[:max_systems]


def pathlib_join(*parts):
    from dynamass.paths import ROOT
    return ROOT.joinpath(*parts)


def main() -> None:
    n_orbits = float(sys.argv[1]) if len(sys.argv) > 1 else 1e5
    n_draws = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_systems = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    tag = depth_tag(n_orbits)
    survey_dir = results_dir(f"resonant{tag}")
    print(f"Depth: {n_orbits:g} inner orbits, {n_draws} draws -> {survey_dir}", flush=True)

    names = resonant_targets(max_systems)
    print(f"{len(names)} resonance-protected systems to attempt", flush=True)

    # Fetch single-reference solutions up front (network I/O); workers stay offline.
    systems, status = {}, []
    for name in names:
        try:
            s = fetch_system_single_ref(name)
            systems[name] = s
            ok = phases_derived(s)
            status.append(dict(system=name, fetched=True, phased=ok, ref=s.ref,
                               note="" if ok else "no fit phases (pitfall 3 or missing tper)"))
            print(f"  [fetched] {name:16s} phased={ok}  ({s.ref})", flush=True)
        except Exception as exc:
            status.append(dict(system=name, fetched=False, phased=False, ref="",
                               note=str(exc)[:80]))
            print(f"  [skip]    {name:16s} {str(exc)[:60]}", flush=True)

    runnable = [s for s in systems.values() if phases_derived(s)]
    print(f"\n{len(runnable)} systems have usable fit phases; integrating", flush=True)

    summaries, todo = [], []
    for s in runnable:
        done_csv = survey_dir / f"{slug(s.name)}_runs.csv"
        if done_csv.exists():
            summ = summarize_system(s, pd.read_csv(done_csv))
            summ["ref"] = getattr(s, "ref", ""); summ["phased"] = True
            summaries.append(summ)
            print(f"  [cached]  {s.name}", flush=True)
        else:
            todo.append(s)

    workers = max(1, (os.cpu_count() or 4) - 2)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(survey_one, s, n_orbits, str(survey_dir), n_draws): s.name for s in todo}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                summ = fut.result()
            except Exception as exc:
                print(f"  [failed]  {name}: {str(exc)[:60]}", flush=True)
                continue
            summaries.append(summ)
            c = summ["ceiling_factor"]
            s90 = summ["edge_on_survival"]
            tag_txt = f"m < {c:.2f}x" if c is not None else "no ceiling"
            flag = "  [EDGE-ON FAIL]" if s90 < 0.5 else ""
            print(f"  [done]    {name:16s} S(90)={s90:.2f} {tag_txt}{flag}", flush=True)

    # Per-planet catalog.
    rows = [
        dict(system=s["system"], planet=p["planet"], msini_mjup=p["msini_mjup"],
             swept=p["swept"], edge_on_survival=s["edge_on_survival"],
             ceiling_factor=s["ceiling_factor"], m95_factor=s["m95_factor"],
             mass_ceiling_mjup=p["mass_ceiling_mjup"], mass_95_mjup=p["mass_95_mjup"],
             inc_floor_deg=s["inc_floor_deg"], t_max_yr=s["t_max_yr"],
             ref=s.get("ref", ""))
        for s in summaries for p in s["planets"]
    ]
    pd.DataFrame(rows).to_csv(results_dir() / f"resonant_catalog{tag}.csv", index=False)
    pd.DataFrame(status).to_csv(results_dir() / f"resonant_status{tag}.csv", index=False)

    n_sys = len({s["system"] for s in summaries})
    n_ceil = sum(1 for s in summaries if s["ceiling_factor"] is not None)
    n_flag = sum(1 for s in summaries if s["edge_on_survival"] < 0.5)
    print(f"\nIntegrated {n_sys} phased systems: {n_ceil} with a ceiling, "
          f"{n_flag} edge-on failures.", flush=True)
    print(f"Wrote resonant_catalog{tag}.csv and resonant_status{tag}.csv", flush=True)


if __name__ == "__main__":
    main()
