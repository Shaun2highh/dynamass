"""Figure for the catalog-artifacts note: Barnard's star survival vs swept
mass factor under three eccentricity treatments of the same catalog entry.
"""

import pandas as pd
from matplotlib import pyplot as plt

from dynamass.paths import results_dir
from dynamass.plotting import BASELINE, GRID, INK, INK_SECONDARY, MUTED, SURFACE, _style_axes
from dynamass.stability import survival_curve

SERIES = [
    ("sampled within uncertainties", "survey_1e6_prod", "#2a78d6"),
    ("forced circular (e = 0)", "survey_1e6_e0", "#1baf7a"),
    ("catalog point estimates", "survey_1e6", "#eda100"),
]

fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=160)
fig.patch.set_facecolor(SURFACE)
_style_axes(ax)

for label, subdir, color in SERIES:
    runs = pd.read_csv(results_dir(subdir) / "barnards_star_runs.csv")
    curve = survival_curve(runs).sort_values("mass_factor")
    ax.plot(
        curve["mass_factor"],
        curve["survival_fraction"],
        color=color,
        linewidth=2,
        marker="o",
        markersize=4.5,
        markeredgecolor=SURFACE,
        markeredgewidth=0.8,
        label=label,
        zorder=3,
    )

ax.set_xscale("log")
ticks = [1, 1.5, 2, 3, 5, 8, 12]
ax.set_xticks(ticks)
ax.set_xticklabels([f"{t:g}x" for t in ticks])
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel("true mass / minimum mass (= 1 / sin i)", color=INK_SECONDARY)
ax.set_ylabel("survival fraction (10$^6$ inner orbits)", color=INK_SECONDARY)
ax.set_title(
    "Barnard's star: one catalog entry, three verdicts",
    color=INK, fontsize=12, loc="left", pad=10,
)
legend = ax.legend(loc="center right", frameon=False, fontsize=9)
for text in legend.get_texts():
    text.set_color(INK_SECONDARY)

fig.tight_layout()
out = results_dir() / "note_fig1_barnard.png"
fig.savefig(out, facecolor=SURFACE)
print(f"Wrote {out}")
