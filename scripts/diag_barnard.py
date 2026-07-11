"""Why is Barnard's star flagged unstable even edge-on at 1e6 orbits?

Compare edge-on (mass_factor = 1) survival with catalog eccentricities vs
forced-circular orbits. If circular survives while catalog-e dies, the flag
is an artifact of eccentricity point estimates, not of the masses.
"""

import copy

from dynamass import fetch_system
from dynamass.integrate import run_one
from dynamass.system import MJUP_PER_MEARTH

N_DRAWS = 8
N_ORBITS = 1e6

system = fetch_system("Barnard's star")
t_max_yr = N_ORBITS * system.min_period_yr
print(f"{system.name}: star {system.star_mass_msun} Msun, t_max = {t_max_yr:,.0f} yr", flush=True)
for p in system.sorted_planets():
    print(
        f"  {p.name}: P = {p.period_days:.3f} d, msini = {p.msini_mjup / MJUP_PER_MEARTH:.2f} Mearth, "
        f"e = {p.ecc:.3f}",
        flush=True,
    )

circular = copy.deepcopy(system)
for p in circular.planets:
    p.ecc = 0.0

for label, sys_variant in [("catalog e", system), ("e = 0", circular)]:
    survived = 0
    for draw in range(N_DRAWS):
        res = run_one(sys_variant, 1.0, t_max_yr, seed=7000 + draw)
        survived += res.survived
        print(
            f"  [{label}] draw {draw}: {res.reason} at t = {res.t_end_yr:,.0f} yr",
            flush=True,
        )
    print(f"{label}: survival {survived}/{N_DRAWS}", flush=True)
