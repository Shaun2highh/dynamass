"""10^7-orbit depth extension for the non-converged production subset.

Selects the systems whose threshold ceiling moved between 10^5 and 10^6
inner orbits (tightened, or newly acquired at depth; flagged systems
excluded — compare_depths.py semantics) and re-runs only those at 10^7
with the same 20 draws (system-name seeds make the draws identical across
depths). Resumable: finished systems are skipped on restart.

Writes results/survey_1e7_prod/<system>_runs.csv and
results/survey_catalog_1e7_prod.csv.

Usage: python scripts/run_depth_extension.py [n_draws]
"""

import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from run_survey import survey_one

from dynamass import fetch_qualifying_systems, fetch_system
from dynamass.paths import results_dir, slug
from dynamass.stability import summarize_system

N_ORBITS = 1e7
LABEL = "prod"


def nonconverged_systems() -> list[str]:
    def ceilings(path):
        df = pd.read_csv(path)
        per = df.groupby("system").agg(
            ceil=("ceiling_factor", "first"), edge=("edge_on_survival", "first")
        )
        return per.ceil, per.edge < 0.5

    shallow, flag_s = ceilings(results_dir() / f"survey_catalog_{LABEL}.csv")
    deep, flag_d = ceilings(results_dir() / f"survey_catalog_1e6_{LABEL}.csv")
    cmp = pd.DataFrame({"f5": shallow, "f6": deep})
    cmp = cmp[~(flag_s | flag_d).reindex(cmp.index, fill_value=False)]
    moved = cmp[
        (cmp.f5.notna() & cmp.f6.notna() & (cmp.f6 < cmp.f5))
        | (cmp.f5.isna() & cmp.f6.notna())
    ]
    return sorted(moved.index)


def main() -> None:
    n_draws = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    subset = nonconverged_systems()
    survey_dir = results_dir(f"survey_1e7_{LABEL}")
    print(f"{len(subset)} non-converged systems -> {survey_dir}", flush=True)
    for name in subset:
        print(f"  {name}", flush=True)

    systems = {s.name: s for s in fetch_qualifying_systems()}

    summaries, todo = [], []
    for hostname in subset:
        system = systems.get(hostname) or fetch_system(hostname)
        done_csv = survey_dir / f"{slug(hostname)}_runs.csv"
        if done_csv.exists():
            summaries.append(summarize_system(system, pd.read_csv(done_csv)))
            print(f"  [cached]  {hostname}", flush=True)
        else:
            todo.append(system)

    workers = max(1, (os.cpu_count() or 4) - 2)  # leave headroom: days-long run on a laptop
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(survey_one, s, N_ORBITS, str(survey_dir), n_draws): s.name
            for s in todo
        }
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
            print(
                f"  [done]    {hostname}: {status}  (+{(time.time() - t0) / 3600:.1f} h)",
                flush=True,
            )

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
    out = results_dir() / f"survey_catalog_1e7_{LABEL}.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nWrote {out} ({len(summaries)} systems)", flush=True)


if __name__ == "__main__":
    main()
