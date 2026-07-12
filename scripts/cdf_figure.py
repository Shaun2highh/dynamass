"""Population figure: cumulative distribution of 95% credible mass factors
across the production catalog, against the isotropy-only baseline (3.20x).
Planets left of the baseline are dynamically tightened.
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from dynamass.paths import results_dir
from dynamass.plotting import BASELINE, INK, INK_SECONDARY, MUTED, SERIES_1, SURFACE, _style_axes

PRIOR_95 = 3.2028  # 1/sin(i) at the isotropic prior's 95th percentile (cos i = 0.95)

deep = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")
c = deep[(deep.mass_95_mjup.notna()) & deep.swept & (deep.edge_on_survival >= 0.5)]
m95 = np.sort(c.m95_factor.to_numpy())
frac = np.arange(1, len(m95) + 1) / len(m95)

fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=160)
fig.patch.set_facecolor(SURFACE)
_style_axes(ax)

ax.step(m95, frac, where="post", color=SERIES_1, linewidth=2, zorder=3)
ax.axvline(PRIOR_95, color=BASELINE, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
ax.annotate(
    "isotropy alone\n(no dynamics)",
    xy=(PRIOR_95, 0.18),
    xytext=(PRIOR_95 * 1.03, 0.18),
    color=MUTED,
    fontsize=9,
    va="center",
)
tightened = float((m95 < 3.0).mean())
ax.annotate(
    f"{tightened:.0%} of planets\ntightened beyond geometry",
    xy=(2.05, 0.62),
    color=INK_SECONDARY,
    fontsize=9,
    ha="center",
)

ax.set_xlim(1.0, 3.6)
ax.set_ylim(0, 1.02)
ax.set_xlabel("95% credible limit on true mass / minimum mass", color=INK_SECONDARY)
ax.set_ylabel("cumulative fraction of planets", color=INK_SECONDARY)
ax.set_title(
    "How much dynamics tightens the mass limits",
    color=INK, fontsize=12, loc="left", pad=10,
)
fig.tight_layout()
out = results_dir() / "m95_cdf_prod.png"
fig.savefig(out, facecolor=SURFACE)
print(f"n = {len(m95)} planets; median m95 = {np.median(m95):.2f}; wrote {out}")
