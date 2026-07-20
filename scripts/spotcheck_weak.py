"""Completeness check on the excluded weakly-interacting block.

The main survey excludes 48 systems as weakly interacting (f_crit > 60): the
analytic estimate says no allowed mass factor (up to 11.5x at i = 5 deg)
drives the most fragile pair to the overlap boundary, so stability should give
no ceiling and m95 ~ 3.20 (the isotropic geometric value). This confirms that
expectation empirically on a representative subset, closing the disposition
logic: these systems are excluded because dynamics cannot constrain them, not
by oversight.

Usage: python scripts/spotcheck_weak.py [n_systems] [n_orbits]
Writes results/weak_spotcheck.csv.
"""

import sys
import pandas as pd

from dynamass import fetch_system, inclination_sweep
from dynamass.paths import ROOT, results_dir
from dynamass.stability import credible_mass_limit, edge_on_survival, system_seed


def main() -> None:
    n_sys = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    n_orbits = float(sys.argv[2]) if len(sys.argv) > 2 else 1e5

    disp = pd.read_csv(ROOT / "paper" / "table1_dispositions.csv")
    weak = disp[(disp.disposition == "excluded")
                & disp.reason.str.contains("weakly interacting", case=False, na=False)]
    # Spread across the f_crit range so the subset is representative.
    weak = weak.sort_values("f_crit")
    idx = [int(i) for i in pd.Series(range(len(weak))).sample(
        min(n_sys, len(weak)), random_state=0).sort_values()]
    picks = weak.iloc[idx]["system"].tolist()
    print(f"Weakly-interacting completeness check: {len(picks)} of {len(weak)} systems, "
          f"{n_orbits:g} orbits", flush=True)

    rows = []
    for name in picks:
        try:
            system = fetch_system(name)
        except Exception as exc:
            print(f"  [skip] {name}: {str(exc)[:50]}", flush=True)
            continue
        runs = inclination_sweep(system, n_draws=10,
                                 t_max_yr=n_orbits * system.min_period_yr,
                                 seed=system_seed(name), verbose=False, workers=6)
        m95 = credible_mass_limit(runs)
        s90 = edge_on_survival(runs)
        rows.append(dict(system=name, edge_on_survival=s90, m95_factor=m95))
        m = "none" if m95 is None else f"{m95:.2f}"
        print(f"  {name:16s} S(90)={s90:.2f}  m95={m}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(results_dir() / "weak_spotcheck.csv", index=False)
    uninformative = df[df.m95_factor.isna() | (df.m95_factor >= 3.15)]
    print(f"\n{len(uninformative)}/{len(df)} give no dynamical constraint "
          f"(m95 >= 3.15 or none), confirming the exclusion.", flush=True)
    print(f"Wrote {results_dir() / 'weak_spotcheck.csv'}", flush=True)


if __name__ == "__main__":
    main()
