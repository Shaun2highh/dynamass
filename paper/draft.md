# Dynamics as a Scale: A Homogeneous Survey of Stability-Derived True-Mass Limits for Non-Transiting Radial-Velocity Exoplanets

*Draft skeleton — v1 numbers; [PROD] marks values to refresh from the
20-draw production catalog (`results/survey_catalog_1e6_prod.csv`).*

## Production numbers (2026-07-13, survey_catalog_1e6_prod.csv — use these for all [PROD] slots)

- 56 systems surveyed (20 draws × 17 inclinations × 1e6 inner orbits); 0 failures.
- Isotropic-prior baseline: with no dynamical information, 95% credibility
  gives m < 3.20× msini for any RV planet. The survey's content is the
  tightening *below* that.
- **61 planets in 23 systems are dynamically tightened (m95 < 3.0×);
  median 95% credible limit among them: 2.68× msini.**
- 25 giants secured below 13 M_Jup at 95% credibility.
- Parameter-fragility flags: GJ 667 C, HIP 57274, Kepler-20.
- Depth convergence (1e5 → 1e6, 20 draws): 9 tightened, 0 loosened, 7 new
  ceilings; third consecutive survey generation with monotone behavior.
- Sensitivity (6 systems × 5 variants; results/sensitivity.csv): limits
  shift ≤ 0.08 under dt/2 and collision radii ×0.5/×0.25; ≤ 0.4 under
  Rayleigh mutual inclinations σ = 2°–5°.
- Highlights: Barnard's star m95 = 2.18×; 47 UMa 2.35×; K2-18 c 2.87×
  (≈ 21.6 M_earth); HD 141399 2.71×.
- Anchors: GJ 876 i > 25° (lit. ≳ 20°, phase-protected); HD 45364
  m95 = 2.29× (Li et al. 2022 fit, phase-agnostic).

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

The radial-velocity method measures a planet's gravitational reflex along
the line of sight only, leaving the orbital inclination i unconstrained
and delivering the minimum mass m sin i rather than the mass. For an
isotropic distribution of orientations the correction is usually modest —
the median of 1/sin i is 1.15, and 95% of orientations imply a true mass
below 3.2 m sin i — but for any individual planet the catalog value is a
floor, not a measurement. The consequences propagate into everything
built on RV masses: mass functions and occurrence rates inherit a
one-sided bias, the planet/brown-dwarf boundary is porous for every giant
whose 1/sin i could exceed ~13 M_Jup / (m sin i), and models of
individual systems' formation and composition rest on lower limits
treated, in practice, as values.

In multi-planet systems, dynamics supplies the missing upper bound. A
coplanar system tilted toward face-on hides planets that are heavier by
1/sin i; heavier planets perturb one another more strongly; and
sufficiently heavy versions destabilize on timescales far shorter than
the systems' ages. Configurations that cannot survive to the present are
excluded, so the survival requirement converts each system's continued
existence into a ceiling on its planets' true masses. The idea is not
new: discovery papers have long applied stability cuts to individual
systems (GJ 876 being the canonical example), and Tamayo, Gilbertson &
Foreman-Mackey (2021) developed stability-constrained characterization
into a general method, applied to the transiting system Kepler-23. What
does not exist is uniformity. Laskar & Petit (2017) classified 131
systems by AMD-stability but did not invert stability into per-planet
mass limits; Volpi et al. (2019) constrained mutual inclinations of ten
RV systems with first-order secular theory; the remaining literature is a
scatter of single-system analyses with mutually incompatible integrators,
instability criteria, timescales, and statistical definitions. No two of
their mass limits are comparable, and no population statement can be
assembled from them.

This paper presents the first homogeneous survey: one pipeline, one
instability criterion, one statistical definition, applied to every
qualifying multi-planet RV system in the NASA Exoplanet Archive, with
orbital parameters sampled within their published uncertainties and the
machinery validated against systems whose stability constraints are
independently known. We report 95% credible true-mass limits under an
isotropic orientation prior for the planets of 56 systems, a byproduct
catalog of parameter-consistency flags, and — as a methodological
contribution in its own right — three classes of catalog artifacts that
dynamical auditing exposes (companion note).

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

### 4.1b HD 45364 anchor
- Li et al. (2022) two-planet solution (3:2 period ratio, low
  eccentricities): the published fit survives 10^5 yr with its own phases;
  the survival cliff is smooth (100% at i ≥ 45°, zero by i ≈ 8.5°), giving
  a 95% credible limit of m < 2.29× msini. Random phases leave survival at
  100% — this fit is stable without phase protection, so the two anchors
  bracket both regimes (phase-protected and phase-agnostic).

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

Three limitations bound the interpretation of the catalog. First, the
sweep is coplanar: the system is tilted as a rigid unit, so mutual
inclinations enter only through the sensitivity variants (§3.2), which
shift the credible limits by at most ~0.4 in the mass factor for
dispersions up to 5°. Strongly non-coplanar architectures — precisely
those the von Zeipel–Lidov–Kozai literature targets — are outside this
survey's assumptions and their limits should be read as conditional on
approximate coplanarity. Second, 10^6 inner orbits is short against Gyr
ages. Every depth comparison we have run — three survey generations —
moved limits monotonically tighter or not at all, so the reported
ceilings are conservative: longer clocks can only strengthen them. The
converse claim (that a surviving configuration is stable forever) is
never made. Third, the inputs are catalog parameters, sampled within
symmetrized published uncertainties rather than refit from radial
velocities. The parameter-fragility flags quantify where this matters
most; for the flagged systems the correct next step is a joint refit, not
a mass limit.

The excluded resonance-protected block (adjacent period ratios within a
few percent of small-integer commensurabilities, screened out at
selection) is addressable with the machinery validated on GJ 876:
single-reference parameter sets carrying fit phases, initialized at the
observed libration. Extending the survey across that block would add
some of the most tightly packed — and therefore most constrainable —
systems in the catalog.

The catalog has immediate uses beyond its headline statement.
Planets whose dynamical ceiling sits close to their m sin i floor are the
best targets for Gaia astrometric confirmation, since their permitted
mass range is narrowest; planets whose ceiling crosses the
deuterium-burning limit are certified planetary without further
observation, cleaning brown-dwarf contamination out of the giant-planet
mass function; and the parameter-fragility flags hand RV teams a
prioritized list of systems whose published solutions their own data no
longer support.

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
