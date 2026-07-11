"""Build the survey target list and rank systems by how quickly the coplanar
mass sweep should hit instability (see dynamass.targets.pair_metrics).
"""

import pandas as pd

from dynamass.paths import results_dir
from dynamass.targets import fetch_qualifying_systems, pair_metrics


def main():
    systems = fetch_qualifying_systems()
    rows = []
    for s in systems:
        f_crit, pair, delta1 = pair_metrics(s)
        rows.append(
            dict(
                system=s.name,
                n_planets=len(s.planets),
                n_swept=sum(p.swept for p in s.planets),
                min_period_d=min(p.period_days for p in s.planets),
                max_ecc=max(p.ecc for p in s.planets),
                delta_hill_at_1x=round(delta1, 2),
                f_crit=round(f_crit, 2),
                fragile_pair=pair,
            )
        )
    df = pd.DataFrame(rows).sort_values("f_crit")
    out = results_dir() / "targets.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} qualifying systems -> {out}\n")
    cols = ["system", "n_planets", "n_swept", "min_period_d", "max_ecc", "delta_hill_at_1x", "f_crit"]
    print(df[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
