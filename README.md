# dynamass — dynamics as a scale

Radial-velocity detections only measure a planet's **minimum mass** (m sin i).
This pipeline uses long-term orbital stability to place **upper limits on the
true masses** of non-transiting RV planets in multi-planet systems — uniformly,
across every qualifying system in the NASA Exoplanet Archive.

**Idea:** tilt a coplanar system toward face-on and every Msini mass scales as
1/sin i. Heavier versions perturb their neighbors harder; versions that
self-destruct in less time than the system's age cannot be the real system.
The surviving region of the inclination sweep is a new constraint: the
*dynamical ceiling* above the RV *mass floor*.

## Layout

- `dynamass/system.py` — data model (Planet, System, mass/inclination conversions)
- `dynamass/targets.py` — target selection via the Exoplanet Archive TAP API
- `dynamass/integrate.py` — one configuration → rebound (WHFast) until close
  encounter (Hill-sphere overlap), escape, or t_max
- `dynamass/stability.py` — inclination sweep → survival grid → mass ceiling
- `dynamass/plotting.py` — survival-curve figure
- `scripts/rank_targets.py` — build + rank the survey target list by predicted
  ceiling (Hill-spacing screen, Gladman criterion; physics in `dynamass.targets`)
- `scripts/run_demo.py` — end-to-end sweep of one system; `--draws/--seed/--incs/
  --tag/--workers` flags cover focused deep runs (e.g. the 47 UMa 1 Myr refinement)

## Quick start

```bash
python -m venv .venv && ./.venv/bin/pip install -e .
./.venv/bin/python scripts/rank_targets.py          # survey target list
./.venv/bin/python scripts/run_demo.py "47 UMa" 100000
```

## First results (2026-07-09/10)

**47 UMa** (3 giant planets, all msini-only), coplanar sweep: at 100 kyr the
ceiling is m < 4.8 × msini; the 1 Myr refinement tightens it to
**m < 3.63 × msini (i > 16°)** — b < 9.2 Mjup, c < 2.0 Mjup, d < 5.9 Mjup.
Longer clocks tighten the ceiling, as the method predicts.

**v0 survey pass** (56 systems, 1e5 inner orbits each, 5 draws x 11
inclinations): 168 planets cataloged, **43 with a dynamical ceiling**
(`results/survey_catalog.csv`, `results/floor_vs_ceiling.png`). Median
ceiling: 4.8 × msini (i > 12°). Six planets have their planetary nature
(< 13 Mjup) secured by dynamics alone. Highlights: Barnard's star and
Kepler-20 g at < 2.67 × msini; GJ 667 C's five planets at < 3.63 × msini.
HIP 57274 is flagged: its catalog parameters are unstable even edge-on
(a consistency flag, not a ceiling). A 1e6-orbit deep pass writes to
`results/survey_1e6/` and `survey_catalog_1e6.csv`.

## v1 (2026-07-11): sampled, validated, flag-aware

- Every run draws star mass, planet masses, periods, eccentricities, and
  periastron angles from symmetrized catalog uncertainties (`integrate._draw`).
- **Validation passed:** the pipeline reproduces GJ 876's literature stability
  constraint (ours i > 25°, literature i ≳ 20°) from the Rivera et al. 2010
  fit, with resonant phases held fixed (`scripts/validate_gj876.py`). Random
  phases drop survival to 12% — resonance protection is real and handled.
- The ceiling criterion is *relative to edge-on survival*; systems whose
  parameters are fragile at any tilt (edge_on_survival < 0.5) are reported as
  **parameter-consistency flags**, not ceilings (GJ 667 C, HD 107148).
- Catalog-artifact classes found and guarded against: eccentricity point
  estimates inconsistent with stability (Barnard's star); pscomppars composite
  rows mixing incompatible fits (use `fetch_system_single_ref` for
  validation-grade parameters); fit epochs stored in `pl_orbtper` (degenerate
  tper guard). Composite-derived phases are never used — survey runs randomize
  phases; only single-reference fits carry them.
- v1 outputs carry a `_v1` suffix (`survey_catalog_v1.csv`,
  `survey_catalog_1e6_v1.csv`, `floor_vs_ceiling_v1.png`,
  `depth_convergence_v1.png`). v0 (unsampled point-estimate) outputs are kept
  for comparison only.

## Remaining caveats

- Coplanar sweep only; mutual-inclination sweeps are the next axis.
- Resonance-protected systems (f_crit ~ 1 block) still excluded from the
  survey band; they need single-reference phase-constrained sweeps (the GJ 876
  machinery exists — applying it across that block is future work).
- Instability proxy is Hill-sphere overlap / escape; no chaos indicators yet.
- Integration times (0.1–1 Myr) are far below system ages (~Gyr); ceilings are
  therefore conservative (the true ceiling is lower). Depth convergence
  (1e5 vs 1e6 orbits) is monotone-tightening, supporting the trend.
- 5 phase/parameter draws per grid point → survival fractions quantized in
  20% steps; the paper run should use ≥ 20 draws.
