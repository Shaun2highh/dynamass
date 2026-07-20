"""Combine the main survey and resonant-block catalogs into the unified
expanded catalog and population figure.

Writes results/combined_catalog.csv (all constrained planets, both blocks,
tagged by block) and results/m95_cdf_combined.png (the cumulative distribution
of 95% credible limits over the full expanded sample).
"""

import pandas as pd

from dynamass.paths import results_dir


def load(path, block):
    df = pd.read_csv(path)
    flagged = df.groupby("system")["edge_on_survival"].first()
    flagged = set(flagged[flagged < 0.5].index)
    con = df[(df["swept"]) & (~df["system"].isin(flagged)) & df["m95_factor"].notna()].copy()
    con["block"] = block
    return con[["system", "planet", "block", "msini_mjup", "m95_factor",
                "mass_95_mjup"]]


def main() -> None:
    main_cat = load(results_dir() / "survey_catalog_1e6_prod.csv", "main")
    reso_cat = load(results_dir() / "resonant_catalog_1e6.csv", "resonant")
    combined = pd.concat([main_cat, reso_cat], ignore_index=True)
    combined = combined.sort_values("m95_factor").reset_index(drop=True)
    out = results_dir() / "combined_catalog.csv"
    combined.to_csv(out, index=False)

    n = len(combined)
    tight = int((combined["m95_factor"] < 3.0).sum())
    print(f"Combined constrained planets: {n} "
          f"({(main_cat.shape[0])} main + {reso_cat.shape[0]} resonant)")
    print(f"  tightened below 3.0x: {tight} ({100*tight/n:.0f}%)")
    print(f"  median (all): {combined['m95_factor'].median():.2f}, "
          f"tightest fifth below {combined['m95_factor'].quantile(0.2):.2f}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots(figsize=(7, 5))
        for block, color in [("main", "#1f77b4"), ("resonant", "#d62728")]:
            v = np.sort(combined[combined["block"] == block]["m95_factor"].to_numpy())
            if len(v):
                ax.plot(v, np.arange(1, len(v) + 1) / len(v), drawstyle="steps-post",
                        color=color, label=f"{block} ({len(v)})")
        allv = np.sort(combined["m95_factor"].to_numpy())
        ax.plot(allv, np.arange(1, len(allv) + 1) / len(allv), drawstyle="steps-post",
                color="0.2", lw=2, label=f"combined ({len(allv)})")
        ax.axvline(3.20, ls="--", color="0.5", lw=1, label="isotropic bound (3.20)")
        ax.set_xlabel(r"95% credible mass factor $m_{95}/m\sin i$")
        ax.set_ylabel("cumulative fraction of planets")
        ax.set_title(f"Expanded catalogue: {n} constrained planets")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(results_dir() / "m95_cdf_combined.png", dpi=150)
        print(f"Wrote {results_dir() / 'm95_cdf_combined.png'}")
    except Exception as exc:
        print(f"(plot skipped: {exc})")

    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
