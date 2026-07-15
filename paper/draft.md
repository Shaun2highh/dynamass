# Dynamics as a Scale: A Homogeneous Survey of Stability-Derived True-Mass Limits for Non-Transiting Radial-Velocity Exoplanets

*Draft v2 (2026-07-14) — all numbers refreshed from the 20-draw production
catalog (`results/survey_catalog_1e6_prod.csv`) and re-verified against it;
remaining [TODO]s: Zenodo DOI, Table 2 excerpt, 10^7-orbit extension.*

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
homogeneous N-body stability survey of 56 multi-planet RV systems
drawn from the NASA Exoplanet Archive, sweeping each system's line-of-sight
inclination and sampling all orbital parameters within their published
uncertainties. We validate the pipeline against GJ 876, recovering the
literature stability constraint (i > 25 deg vs. published i ≳ 20 deg). We
report 95% credible true-mass upper limits under an isotropic orientation
prior for 123 planets in 53 systems: 61 planets in 23 systems are
tightened below 3.0 times their minimum masses (median limit 2.68× among
them), and 25 giant planets are certified below the deuterium-burning
limit by dynamics alone. As a byproduct, the survey
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
dynamical auditing exposes (companion note, submitted to RNAAS 2026
July 14).

## 2. Sample selection

We select systems from the NASA Exoplanet Archive's composite parameters
table (pscomppars, accessed 2026 July 9–13) requiring at least two
planets, periods and masses for all of them, a stellar mass, and at least
one non-transiting planet whose mass provenance is Msini — the planets
the survey can constrain. Because dynamical interactions weaken steeply
with separation, we further require at least one adjacent pair with a
period ratio below 6. This yields 148 qualifying systems.

Each system is ranked by an analytic pre-estimate of where its ceiling
should lie: the swept mass factor f_crit at which the most fragile
adjacent pair, with masses scaled by f and separations measured in mutual
Hill radii (eccentricity-reduced), reaches the two-planet overlap
criterion Δ = 2√3 (Gladman 1993). Multi-planet systems destabilize at
wider spacings, so f_crit is conservative. The survey band takes
f_crit ∈ (1.05, 60) with e_max ≤ 0.75 and P_inner ≥ 1.5 d — 56 systems.
The excluded f_crit ≈ 1 block is dominated by resonance-protected pairs
whose survival depends on phase coherence that composite catalog
parameters cannot supply (§3.4, §6); it is deferred rather than
constrained. Table 1 (`paper/table1_dispositions.csv`, machine-generated
by `scripts/make_table1.py`) gives the full disposition of all 148
systems: 53 surveyed, 3 flagged, and 92 excluded (42 resonance-protected,
48 too weakly interacting for dynamics to bite at any allowed mass, and 9
with sub-1.5-day inner periods, categories overlapping).

## 3. Methods

### 3.1 Configuration sampling

A coplanar system tilted rigidly with respect to the line of sight leaves
its internal dynamics unchanged while every Msini mass scales as 1/sin i;
we therefore sweep i over a 17-point grid from 90° (edge-on, masses at
their floors) to 5° (masses at 11.5× the floors), holding planets with
transiting or astrometric true masses fixed. At each grid point we
integrate 20 independent realizations, drawing the stellar mass and every
planet's mass, period, eccentricity, and periastron longitude from
truncated normal distributions built on the symmetrized catalog 1σ
uncertainties (point values where errors are unreported; eccentricities
truncated to [0, 0.95]). Unknown angles are drawn uniformly. Orbital
phases are randomized for composite-catalog systems and taken from the
fit's time of periastron only for single-reference parameter sets, for
the reasons documented in §3.4.

### 3.2 Integration and instability criterion

Realizations are integrated with REBOUND's WHFast with timestep
dt = min_p P_p (1−e_p)^{3/2} / 20, resolving the fastest perihelion
passage. Instability is a close encounter within the sum of Hill radii
(particles carry their Hill radius as collision radius) or escape beyond
20 times the widest semi-major axis. Integration time is uniform in
inner-planet orbits — 10^5 and 10^6 for the two survey depths — making
the effort per system architecture-independent; convergence between the
depths is examined in §4.3. Sensitivity of the final limits to these
choices is quantified on a six-system representative subset spanning the
survey's architectures: halving dt changes 95% credible limits by ≤ 0.03
in the mass factor; collision radii scaled to 0.5× and 0.25× the Hill
radius change them by ≤ 0.08; replacing exact coplanarity with mutual
inclinations drawn from Rayleigh distributions of σ = 2° and 5° changes
them by ≤ 0.4 (results/sensitivity.csv). None approaches the survey's
grid resolution in i.

### 3.3 Statistical definitions

Each system yields a survival curve S(i), the fraction of realizations
surviving to t_max at inclination i. Because parameter draws can be
fragile at any tilt, constraints are defined relative to the edge-on
baseline: systems with S(90°) < 0.5 are reported as
parameter-consistency flags — statements about the published parameters,
not mass limits. For unflagged systems the primary statistic is the 95%
credible limit on the mass factor under an isotropic orientation prior
(uniform in cos i), with posterior density proportional to S(i): the
factor below which 95% of the surviving posterior lies. With no
dynamical information this limit is 3.20 for every RV planet; the
survey's information content is the tightening below that value. A
secondary threshold ceiling (smallest factor with S < 0.5 × S(90°)) is
tabulated for comparison with prior single-system work.

### 3.4 Catalog-artifact classes found and guarded
1. Eccentricity point-estimates dynamically inconsistent with system
   survival (Barnard's star: e = 0.03–0.08 kills the system in kyr;
   e drawn within errors resolves it).
2. Composite tables (pscomppars) mix parameters across incompatible fits —
   fatal for phase-coherent (resonant) initialization.
3. Fit epochs stored in the time-of-periastron column (GJ 876/Rivera
   2010), producing degenerate all-simultaneous-periastron phases.

## 4. Validation

The pipeline is validated against two systems whose stability constraints
are independently known, chosen to bracket the two dynamical regimes the
survey encounters: a resonance-protected system whose survival depends on
its orbital phases (GJ 876) and a near-resonant system that is stable
regardless of them (HD 45364).

### 4.1 GJ 876: the phase-protected anchor

GJ 876 is the canonical stability-constrained system. The Archive's
default solution is the coplanar dynamical fit of Rivera et al. (2010) at
i = 59°: true masses, with the phases of the 4:2:1 Laplace resonance at
their libration center. We reconstruct the equivalent minimum-mass system
by scaling the fitted masses by sin 59°, fix the mean anomalies at the
fit epoch to the published values (their Table 3 — the Archive's
time-of-periastron column stores the epoch itself for this reference,
artifact Class 3 of §3.4, so phases cannot be derived from it), and sweep
a 13-point inclination grid with phases held fixed (5 draws per point,
5,000 yr per realization ≈ 10^6 inner-planet orbits).

The validation makes three independent demands. First, the published
configuration, entering the sweep at mass factor 1/sin 59° = 1.17, must
survive: it does. Second, the recovered constraint must match the
literature: survival is zero at every grid inclination at or below 25°
and recovers above it, giving i > 25° (m < 2.37× msini) against the
published i ≳ 20° — consistent, and conservative in the safe direction.
Third, the same masses with randomized phases must not reliably survive,
or phase protection would be irrelevant to the problem: survival
collapses to 12%. The resonance protection is real, and the
phase-constrained initialization captures it.

### 4.2 HD 45364: the phase-agnostic anchor

HD 45364 anchors the opposite regime. Its two giants sit in a 3:2
commensurability with low eccentricities, and the Li et al. (2022)
solution is stable without phase assistance: initialized with the fit's
own phases, the published configuration survives the full 10^5 yr
integration, and randomizing the phases leaves survival at 100% — the
constraint owes nothing to resonance protection. The survival cliff is
correspondingly smooth rather than resonance-sharpened: complete survival
for i ≥ 45°, declining to zero by i ≈ 8.5° (17-point grid, 10 draws per
point), integrating under the isotropic prior to a 95% credible limit of
m < 2.29× msini. Together the anchors bracket the survey population — one
ceiling that exists because of its phases, one indifferent to them — and
the same pipeline recovers both with no per-system tuning.

### 4.3 Depth convergence

A survey whose limits depended on integration length would be reporting
its clock, not the dynamics. Every system therefore runs at two depths,
10^5 and 10^6 inner orbits, with identical parameter draws (seeds keyed
to the system name), and the threshold ceilings are compared. Deeper
integration can only reveal instability, never undo it, so ceilings must
move one way — and they do: among the 53 unflagged systems (flagged
systems excluded at either depth), 9 ceilings tightened, 5 held exactly,
none loosened, and 7 systems acquired a ceiling only at 10^6 (Figure:
depth_convergence_prod.png). This is the third consecutive survey
generation with strictly monotone behavior, and it is what makes the
reported limits conservative: a longer clock can only strengthen them
(§6). [PENDING: 10^7-orbit extension of the 16 non-converged systems —
run launched 2026-07-14, results/survey_catalog_1e7_prod.csv.]

## 5. Results

### 5.1 The catalog

Of the 56 surveyed systems, 53 pass the edge-on consistency test and
yield 95% credible mass limits for 123 non-transiting planets. Sixty-one
planets in 23 systems are dynamically tightened below 3.0× their minimum
masses — meaningfully inside the 3.20× that isotropy alone guarantees —
with a median limit of 2.68× among them (Figure: floor_vs_ceiling_final).
Twenty-five giants whose face-on orientations would have exceeded the
deuterium-burning limit are certified planetary at 95% credibility.
Individual highlights: Barnard's star's four sub-Earths are capped at
2.18× their minimum masses; 47 UMa at 2.35×; HD 141399's four giants at
2.71×; and K2-18 c, the non-transiting companion of the habitable-zone
sub-Neptune K2-18 b, at 2.87× ≈ 21.6 M_earth, excluding a giant-planet
identity. The tightest factor in the catalog is a caution against
conflating the two headline statistics: TYC 1422-614-1's pair is capped
at 2.01× — the survey's strongest relative constraint — yet planet c's
minimum mass of 10 M_Jup puts even that ceiling at ≈20 M_Jup, above the
deuterium-burning limit. A tight mass factor and a certified planetary
identity are independent properties.

### 5.2 Population statement

The cumulative distribution of credible limits (Figure: m95_cdf_prod)
answers the survey's title question: exactly half the qualifying planets
(61 of 123) have their permitted mass range tightened beyond geometry,
the tightest fifth to below ~2.6×, and no limit exceeds the isotropic
bound beyond the inclination grid's discretization (the single nominal
exception, TOI-1062 c at 3.22× against the analytic 3.20×, is an
unconstrained posterior rendered on the 17-point grid) — dynamics only
ever removes orientations. Read as demographics:
for packed multi-planet RV systems, the "hidden monster" tail of the
minimum-mass distribution is largely a geometric fiction; the surviving
configurations concentrate near edge-on masses.

### 5.3 Parameter-fragility flags

Three systems fail the edge-on consistency test in more than half their
parameter draws: GJ 667 C, HIP 57274, and Kepler-20. These are
data-quality results, not mass limits: the published parameter sets, with
their stated uncertainties, do not support long-lived configurations at
any tilt. For GJ 667 C this echoes the long-standing dispute over its
planet multiplicity; for the others it flags eccentricity solutions that
their own dynamics reject. A joint dynamical–RV refit is the indicated
follow-up in all three cases.

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

- Code: https://github.com/Shaun2highh/dynamass. Catalogs + per-run
  records archived at Zenodo [TODO DOI — mint after RNAAS note acceptance].
  NASA Exoplanet Archive (pscomppars DOI: 10.26133/NEA13, ps DOI:
  10.26133/NEA12) accessed 2026 July 9–13.

## Tables

1. System dispositions (148 rows: surveyed / flagged / excluded + reason,
   edge-on survival, m95) — `paper/table1_dispositions.csv`, regenerate
   with `scripts/make_table1.py`.
2. Per-planet true-mass limits (123 rows: msini, 95% credible factor and
   mass, threshold ceiling, inclination floor; sorted tightest-first) —
   `paper/table2_planet_limits.csv`, regenerate with
   `scripts/make_table2.py`. Journal excerpt: the ~10 tightest rows;
   full machine-readable version from `results/survey_catalog_1e6_prod.csv`.

## Figures (current files)

1. Survival curve example / validation — `results/gj_876_validation.png`,
   `results/hd_45364_validation.png`
2. Floor vs ceiling dumbbells (95% credible, flags excluded) —
   `results/floor_vs_ceiling_final.png`
3. Depth convergence (production) — `results/depth_convergence_prod.png`
4. Cumulative distribution of credible limits — `results/m95_cdf_prod.png`
5. Barnard eccentricity artifact (three treatments) —
   `results/note_fig1_barnard.png` (shared with the companion note)
