# Dynamics as a Scale: A Homogeneous Survey of Stability-Derived True-Mass Limits for Non-Transiting Radial-Velocity Exoplanets

*Draft skeleton — v1 numbers; [PROD] marks values to refresh from the
20-draw production catalog (`results/survey_catalog_1e6_prod.csv`).*

## Abstract (draft)

Radial-velocity detections constrain only the minimum mass m sin i of a
planet; the true mass can exceed it by an arbitrary factor for face-on
orbits. In multi-planet systems, however, long-term dynamical stability
bounds that factor: heavier, more face-on configurations perturb their
neighbors strongly enough to self-destruct within the system's lifetime.
Discovery papers occasionally apply this constraint to individual systems
with heterogeneous methods; no uniform survey exists. We present a
homogeneous N-body stability survey of [PROD: 56] multi-planet RV systems
drawn from the NASA Exoplanet Archive, sweeping each system's line-of-sight
inclination and sampling all orbital parameters within their published
uncertainties. We validate the pipeline against GJ 876, recovering the
literature stability constraint (i > 25 deg vs. published i ≳ 20 deg). We
report 95% credible true-mass upper limits under an isotropic orientation
prior for [PROD: 61] planets in [PROD: 25] systems, with a median limit of
[PROD: ~4.8]× the minimum mass, and certify [PROD: 9] giant planets below
the deuterium-burning limit by dynamics alone. As a byproduct, the survey
identifies three classes of catalog-parameter artifacts that dynamical
consistency exposes, including published eccentricity point-estimates
incompatible with the survival of their own systems.

## 1. Introduction

- The m sin i degeneracy; population consequences (mass functions,
  occurrence rates, brown-dwarf contamination).
- Prior work and the gap:
  - Tamayo, Gilbertson & Foreman-Mackey (2021): stability-constrained
    characterization, single transiting system (Kepler-23) — method, not
    survey (arXiv:2009.11831).
  - Laskar & Petit (2017): AMD-stability classification of 131 systems —
    population-scale but analytic and not inverted into mass limits
    (arXiv:1703.07125).
  - Volpi et al. (2019): 3D secular dynamics of 10 RV systems —
    inclination constraints, secular theory, small sample
    (arXiv:1905.03722).
  - Single-system dynamical analyses (GJ 876; HD 10180; GJ 581; HD 41004)
    — heterogeneous methods, no uniformity.
- This work: one machine, every qualifying system, one statistical
  definition, with validation.

## 2. Sample selection

- NASA Exoplanet Archive pscomppars; ≥2 planets, all with periods and
  masses; star mass known; ≥1 non-transiting Msini planet; adjacent period
  ratio < 6. → 148 qualifying systems ranked by an analytic Hill-spacing
  screen (f_crit; Gladman 1993 overlap criterion scaled by the swept mass
  factor).
- v1 band: f_crit ∈ (1.05, 60), e_max ≤ 0.75, P_inner ≥ 1.5 d → 56
  systems. Resonance-protected block (f_crit ≈ 1) deferred to
  phase-constrained treatment (§5.3).
- Table 1: full disposition table (surveyed / flagged / excluded, with
  reasons). [TODO: generate from targets.csv + catalog]

## 3. Methods

### 3.1 Configuration sampling
- Coplanar sweep: line-of-sight inclination i ∈ [5°, 90°], 17-point grid;
  all Msini masses scale as 1/sin i; transiting/astrometric true masses
  fixed.
- Parameter draws: star mass, planet masses, periods, eccentricities,
  periastron longitudes from symmetrized catalog 1σ errors (truncated
  normals); unknown angles uniform. [PROD: 20] draws per grid point.
- Phases: randomized for composite-catalog systems; derived from the fit's
  time of periastron only for single-reference parameter sets (§3.4).

### 3.2 Integration and instability criterion
- REBOUND WHFast; dt = min over planets of P(1−e)^1.5/20; instability =
  Hill-sphere overlap (collision radius = Hill radius) or escape (r > 20
  a_max); t_max uniform in inner-planet orbits (10^5 and 10^6; convergence
  in §4.2).
- [TODO sensitivity subsection: dt/2, collision radius ×0.5/×0.25,
  Rayleigh mutual inclinations σ = 2°, 5° on a representative subset.]

### 3.3 Statistical definitions
- Survival curve S(i); parameter-fragility flag if S(edge-on) < 0.5
  (consistency result, not a mass limit).
- Threshold ceiling: smallest factor with S < 0.5 × S(edge-on).
- Primary statistic: 95% credible mass limit under isotropic prior
  (uniform in cos i), posterior ∝ S(i) d(cos i).

### 3.4 Catalog-artifact classes found and guarded
1. Eccentricity point-estimates dynamically inconsistent with system
   survival (Barnard's star: e = 0.03–0.08 kills the system in kyr;
   e drawn within errors resolves it).
2. Composite tables (pscomppars) mix parameters across incompatible fits —
   fatal for phase-coherent (resonant) initialization.
3. Fit epochs stored in the time-of-periastron column (GJ 876/Rivera
   2010), producing degenerate all-simultaneous-periastron phases.

## 4. Validation

### 4.1 GJ 876 anchor
- Rivera et al. (2010) coplanar fit (Table 3 elements, phases at the
  libration center): survives; sweep yields i > 25° vs literature i ≳ 20°;
  random phases collapse survival to 12% — resonance protection is real
  and correctly handled.
- [TODO: second anchor — HD 128311 or HD 45364.]

### 4.2 Depth convergence
- 10^5 → 10^6 inner orbits: ceilings only tighten or hold (v1: 5
  tightened, 0 loosened, 8 new); Figure: depth_convergence_v1.png.
- [TODO: 10^7-orbit extension for the non-converged subset.]

## 5. Results

### 5.1 The catalog
- [PROD] planets with 95% credible limits; median factor [PROD];
  headline figure: floor_vs_ceiling (msini dot → ceiling tick, deuterium
  line).
- Notable systems: K2-18 c (< 2.4× msini ≈ [PROD] M_earth); Barnard's
  star (all four < 2.4× msini); Kepler-20 g; nine giants secured below
  13 M_Jup.

### 5.2 Population statement
- Cumulative distribution of credible mass factors; comparison with the
  isotropic-prior expectation (what fraction of the sin-i tail dynamics
  removes). [TODO figure]

### 5.3 Parameter-fragility flags
- 47 UMa, GJ 667 C, HD 107148: catalog parameters unstable at any tilt in
  ≥ half of draws — dynamical consistency as a data-quality audit.

## 6. Discussion

- Caveats: coplanarity, integration depth vs system age (mitigated by
  monotone convergence), Hill-overlap proxy, catalog dependence.
- The resonant block: path to phase-constrained sweeps via
  single-reference fits.
- Uses: prioritizing astrometric follow-up (Gaia DR4), cleaning mass
  functions, brown-dwarf boundary demographics.

## 7. Data availability

- Code: github.com/[TODO] (dynamass). Catalogs + per-run records archived
  at Zenodo [TODO DOI]. NASA Exoplanet Archive accessed 2026-07-09..12.

## Figures (current files)

1. Survival curve example (47 UMa v0 / GJ 876 validation) —
   `results/gj_876_validation.png`
2. Floor vs ceiling dumbbells — `results/floor_vs_ceiling_1e6_v1.png`
   [PROD refresh; exclude flagged systems]
3. Depth convergence — `results/depth_convergence_v1.png` [PROD refresh]
4. [TODO] Cumulative distribution of credible mass factors
5. [TODO] Barnard eccentricity artifact illustration (catalog-e vs e=0
   survival vs sampled)
