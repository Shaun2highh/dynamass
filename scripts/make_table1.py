"""Table 1: disposition of every qualifying system (surveyed / flagged /
excluded with reason), from results/targets.csv + the production catalog.

Writes paper/table1_dispositions.csv and a compact markdown preview.
"""

import pandas as pd

from dynamass.paths import ROOT, results_dir

F_CRIT_MIN, F_CRIT_MAX = 1.05, 60.0
MAX_ECC, MIN_PERIOD_D = 0.75, 1.5

targets = pd.read_csv(results_dir() / "targets.csv")
prod = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")
per_system = prod.groupby("system").agg(
    edge=("edge_on_survival", "first"), m95=("m95_factor", "first")
)


def disposition(row):
    if row.system in per_system.index:
        s = per_system.loc[row.system]
        if s.edge < 0.5:
            return "flagged", "parameters unstable at any tilt in >=50% of draws", s.edge, s.m95
        return "surveyed", "", s.edge, s.m95
    reasons = []
    if row.f_crit < F_CRIT_MIN:
        reasons.append("resonance-protected / at stability limit (f_crit ~ 1)")
    if row.f_crit > F_CRIT_MAX:
        reasons.append(f"weakly interacting (f_crit > {F_CRIT_MAX:g})")
    if row.max_ecc > MAX_ECC:
        reasons.append(f"e_max > {MAX_ECC}")
    if row.min_period_d < MIN_PERIOD_D:
        reasons.append(f"P_inner < {MIN_PERIOD_D} d")
    return "excluded", "; ".join(reasons) or "outside survey band", None, None


rows = []
for _, r in targets.iterrows():
    disp, reason, edge, m95 = disposition(r)
    rows.append(
        dict(
            system=r.system,
            n_planets=r.n_planets,
            n_swept=r.n_swept,
            f_crit=r.f_crit,
            disposition=disp,
            reason=reason,
            edge_on_survival=None if edge is None else round(float(edge), 2),
            m95_factor=None if m95 is None else round(float(m95), 2),
        )
    )

df = pd.DataFrame(rows).sort_values(["disposition", "f_crit"])
out = ROOT / "paper" / "table1_dispositions.csv"
df.to_csv(out, index=False)

counts = df.disposition.value_counts()
print(f"{len(df)} systems: {counts.to_dict()}")
reasons = df[df.disposition == "excluded"].reason.value_counts()
print("\nexclusion reasons:")
print(reasons.to_string())
print(f"\nWrote {out}")
