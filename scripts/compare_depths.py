"""Depth-convergence comparison: per-system ceilings at 1e5 vs 1e6 orbits.

Usage: python scripts/compare_depths.py [label]
E.g. `compare_depths.py v1` compares survey_catalog_v1.csv with
survey_catalog_1e6_v1.csv. Systems flagged parameter-fragile (edge-on
survival < 0.5 at either depth, or first-grid-step ceilings in v0 catalogs
that lack the column) are excluded — they are consistency results, not
ceilings.
"""

import sys

import pandas as pd

from dynamass.paths import results_dir
from dynamass.plotting import plot_depth_convergence

SWEEP_MAX = 11.47  # deepest mass factor in the default inclination grid (i = 5 deg)
LEGACY_FLAG_THRESHOLD = 1.07  # first grid step, for catalogs without edge_on_survival


def load(path):
    df = pd.read_csv(path)
    per_system = df.groupby("system").agg(
        ceil=("ceiling_factor", "first"),
        edge=("edge_on_survival", "first") if "edge_on_survival" in df else ("ceiling_factor", "size"),
    )
    if "edge_on_survival" in df:
        flagged = per_system.edge < 0.5
    else:
        flagged = per_system.ceil <= LEGACY_FLAG_THRESHOLD
    return per_system.ceil, flagged


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else ""
    suffix = f"_{label}" if label else ""
    shallow, flag_s = load(results_dir() / f"survey_catalog{suffix}.csv")
    deep, flag_d = load(results_dir() / f"survey_catalog_1e6{suffix}.csv")

    cmp = pd.DataFrame({"f_shallow": shallow, "f_deep": deep})
    flags = cmp.index[(flag_s | flag_d).reindex(cmp.index, fill_value=False)].tolist()
    cmp = cmp[~cmp.index.isin(flags)]

    out = results_dir() / f"depth_convergence{suffix}.png"
    plot_depth_convergence(cmp, ("100k inner orbits", "1M inner orbits"), SWEEP_MAX, str(out))

    both = cmp.dropna()
    print(f"systems with a deep ceiling: {int(cmp.f_deep.notna().sum())} / {len(cmp)}")
    print(
        f"tightened: {int((both.f_deep < both.f_shallow).sum())}, "
        f"loosened: {int((both.f_deep > both.f_shallow).sum())}, "
        f"unchanged: {int((both.f_deep == both.f_shallow).sum())}"
    )
    print(f"new ceilings at depth: {int((cmp.f_shallow.isna() & cmp.f_deep.notna()).sum())}")
    print(f"flagged (excluded): {flags}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
