"""Table 2: per-planet true-mass limits for the surveyed systems, from the
production catalog. Swept (Msini-only) planets of unflagged systems only —
the 123 planets for which the survey constrains the mass.

Writes paper/table2_planet_limits.csv and prints the tightest-limit rows
as a compact preview for the journal excerpt.
"""

import pandas as pd

from dynamass.paths import ROOT, results_dir

MEARTH_PER_MJUP = 317.8
TIGHT_FACTOR = 3.0  # tightened = meaningfully inside the isotropic 3.20

prod = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")

edge = prod.groupby("system")["edge_on_survival"].first()
flagged = set(edge[edge < 0.5].index)
df = prod[~prod["system"].isin(flagged) & prod["swept"]].copy()

df["msini_mearth"] = df["msini_mjup"] * MEARTH_PER_MJUP
df["mass_95_mearth"] = df["mass_95_mjup"] * MEARTH_PER_MJUP
df["tightened"] = df["m95_factor"] < TIGHT_FACTOR

cols = dict(
    system=df["system"],
    planet=df["planet"],
    msini_mjup=df["msini_mjup"].map("{:.4g}".format),
    msini_mearth=df["msini_mearth"].map("{:.4g}".format),
    m95_factor=df["m95_factor"].round(2),
    mass_95_mjup=df["mass_95_mjup"].map("{:.4g}".format),
    mass_95_mearth=df["mass_95_mearth"].map("{:.4g}".format),
    ceiling_factor=df["ceiling_factor"].round(2),
    inc_floor_deg=df["inc_floor_deg"].round(1),
    tightened=df["tightened"],
)
out_df = pd.DataFrame(cols).sort_values(["m95_factor", "system", "planet"])

out = ROOT / "paper" / "table2_planet_limits.csv"
out_df.to_csv(out, index=False)

n_tight = int(out_df.tightened.sum())
print(
    f"{len(out_df)} planets in {out_df.system.nunique()} systems; "
    f"{n_tight} tightened (< {TIGHT_FACTOR}x), "
    f"median m95 among them {out_df[out_df.tightened].m95_factor.median():.2f}x"
)
print("\ntightest 10 (journal excerpt candidates):")
print(
    out_df.head(10)[
        ["system", "planet", "msini_mearth", "m95_factor", "mass_95_mearth"]
    ].to_string(index=False)
)
print(f"\nWrote {out}")
