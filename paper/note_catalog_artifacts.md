# Dynamical Stability Audits Expose Three Classes of Parameter Artifacts in Exoplanet Catalogs

*Target: AAS Research Notes (≤1000 words, 1 figure).*
*CANONICAL SUBMISSION FILE: `note_catalog_artifacts.tex` (polished 2026-07-13;
626 body words). This markdown is the reading copy and may lag it.
Submission steps: `paper/SUBMIT.md`.*

Aggregated exoplanet catalogs — above all the NASA Exoplanet Archive —
are the de facto input for population studies, dynamical analyses, and
target selection. During a homogeneous N-body stability survey of
multi-planet radial-velocity systems, we found that requiring a system's
own long-term survival is a sharp, cheap audit of its published
parameters: configurations drawn directly from the catalog sometimes
self-destruct on timescales of 10^3–10^4 orbits, which is impossible for
systems observed to be Gyr old. Chasing every such contradiction to its
root exposed three distinct, recurring artifact classes. We report them
so that other users of these catalogs can guard against them; none is
hypothetical — each broke a real analysis before being diagnosed.

**Class 1: eccentricity point estimates that are dynamically fatal noise.**
Compact low-mass systems are typically fit with small, poorly constrained
eccentricities whose posteriors are consistent with zero; the catalog
nonetheless records nonzero point values. Barnard's star is the extreme
case: its four sub-Earth planets (periods 2.3–6.7 d) carry catalog
eccentricities of e = 0.03–0.08 with 1σ uncertainties of the same size
(e.g., e = 0.040 ± 0.040). Integrated as written, the system destroys
itself through close encounters within 1,400–4,300 yr in every
realization; with the same entry forced circular, every realization
survives 10^6 inner orbits (Figure 1). Neither extreme is the right
treatment: drawing eccentricities from their published uncertainties
(truncated at zero) yields intermediate survival and propagates the
parameter ignorance honestly. The general lesson is that for dynamically
packed systems, catalog eccentricity point values must be treated as
draws from a distribution, never as facts; stability results computed
from the point values alone can be qualitatively wrong in either
direction.

**Class 2: composite tables mix parameters from incompatible fits.**
The Archive's `pscomppars` table assembles each parameter from the
"best available" reference per column, so a single system's row set can
combine periods from one paper with eccentricities, periastron angles,
and periastron times from others. For secularly evolving systems the
elements of different epochs and different fits are not mutually
consistent, and for resonant or near-resonant systems the damage is
acute: orbital phases assembled across references imply precise timing
relationships that no fit ever measured. In our survey, phases derived
from composite periastron times falsely collapsed the stable systems
47 UMa and HD 141399 to near-total instability at their minimum masses.
Dynamical work requires self-consistent parameter sets from a single
reference (the Archive's `ps` table filtered to one `pl_refname`);
composite rows are safe only when phase information is discarded and
parameters are sampled within uncertainties.

**Class 3: fit epochs stored as times of periastron.** For some
references the Archive's `pl_orbtper` column contains the *epoch of the
fit* rather than each planet's periastron passage time. GJ 876 (Rivera
et al. 2010) is reported with `pl_orbtper` = 2450602.093 for all four
planets — the fit epoch — which, read literally, places every planet at
periastron simultaneously. Phases derived from such degenerate values
initialized the famous 2:1 Laplace resonance far from its libration
center, and the reconstructed system — stable in every published
analysis — was destroyed within 5,000 yr even under an exact (IAS15)
integration. The correct mean anomalies (355°, 294.59°, 325.7°, 335° at
that epoch; Rivera et al. 2010, Table 3) restore libration and long-term
stability. Identical periastron times across a multi-planet system are a
reliable signature of this artifact and should be rejected before phase
information is used.

**Recommendations.** (1) Treat catalog eccentricities of compact systems
as distributions bounded below by zero; report stability conclusions
marginalized over them. (2) Never derive orbital phases from composite
tables; use single-reference parameter sets for any phase-sensitive
dynamics. (3) Reject periastron times that are identical across planets.
(4) Archives could flag columns whose values are epochs rather than
measurements, and offer a "dynamically self-consistent" view that
guarantees single-reference provenance. Each check costs seconds; the
failures they prevent masquerade convincingly as science.

All integrations used REBOUND/WHFast with instability defined by
Hill-sphere overlap or escape; full code, per-run records, and the survey
from which these cases emerged are available at [repository/Zenodo DOI].

**Figure 1.** Survival fraction of Barnard's star realizations versus the
swept mass factor 1/sin i, integrated for 10^6 inner-planet orbits under
three treatments of the same catalog entry: eccentricities drawn within
published uncertainties (blue), forced circular (green), and catalog
point estimates (yellow). The point-estimate treatment destroys the
system even at minimum masses; the circular treatment is stable nearly
everywhere; sampling propagates the uncertainty honestly. File:
`results/note_fig1_barnard.png`.

**References.** Rivera et al. 2010, ApJ 719, 890 · NASA Exoplanet
Archive (pscomppars, ps; accessed 2026 July 9–13) · Rein & Liu 2012
(REBOUND) · Rein & Tamayo 2015 (WHFast). [Complete on submission.]
