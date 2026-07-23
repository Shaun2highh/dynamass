# Expansion results log — every number, with the script and file that made it

Running ledger for the 2026-07 research expansion. Each entry names the
producing script and the output file, so any figure in the manuscript can
be traced to its origin. Surfaces in the vault through the `dynamass/paper`
symlink. Related: [[dynamass/paper/draft|draft]],
[[dynamass/paper/resonant_flags_validation|resonant flags]],
[[literature/index|literature library]].

## 2026-07-19/20 — Part A: resonant block (`scripts/run_resonant.py`)

Ran the 43 resonance-protected systems the main survey excludes, with the
phase-coherent machinery (`fetch_system_single_ref`: single reference +
fit phases at libration, validated on GJ 876). Depth 1e6, 20 draws.

- 22 of 43 have a usable single reference (rest lack one; recorded in
  `results/resonant_status_1e6.csv`, not forced).
- **21 constrained planets in 9 clean systems**, median m95 `2.28x`
  (tighter than the main survey's `2.68x`, as expected for packed systems).
- **13 flagged systems** (published fit unstable even edge-on). All 12
  original 1e5 flags persisted at 10x depth; limits monotone, none loosened.
- Source: `results/resonant_catalog_1e6.csv`.

## 2026-07-19 — resonant flag literature check

The 13 edge-on flags are not artifacts. BD+20 2457 (Horner & Wittenmyer
2014, [[literature/index|`1401.2793`]]), HD 47366 (Marshall+2019,
`1811.06476`), HD 200964, HD 33844 all independently documented as
dynamically problematic. Full table in
[[dynamass/paper/resonant_flags_validation|resonant_flags_validation]].

## 2026-07-19 — non-coplanar dimension (`scripts/run_mutual_inc.py`)

10 architecture-spanning systems x sigma_mut 0-30 deg. Source
`results/mutual_inc.{csv,png}`.

- Limits robust to modest non-coplanarity: m95 shifts `<0.3` from coplanar
  to sigma=10 deg, often *tightens* (close-encounter detuning).
- At sigma >= 20-30 deg systems fail edge-on (47 UMa `0.7 -> 0.1`), so
  stability caps the mutual inclination.

## 2026-07-20 — weakly-interacting completeness (`scripts/spotcheck_weak.py`)

8 of the 48 excluded weak systems (f_crit > 60), 1e5 orbits. All 8 return
m95 `= 3.20` exactly (the isotropic geometric bound, no dynamical info),
confirming the exclusion empirically. Source `results/weak_spotcheck.csv`.

## 2026-07-22 — bibliography verified (Crossref DOI metadata)

Every `\bibitem` checked against Crossref. Filled: Basant+2025 = `ApJL 982,
L1`; Qin+2025 = `ApJL 988, L37`. All other volumes/pages confirmed correct.
14 reference PDFs downloaded to `literature/pdfs/` (arXiv IDs resolved by
title lookup, not memory; one wrong-paper match caught and corrected —
see [[literature/index|index]] provenance note).

## 2026-07-23 — Part B extended: PMA cross-check (`scripts/validate_pma.py`)

Kervella+2022 Hipparcos-Gaia proper-motion anomalies, `43 of 56` hosts
(vs 4 for Feng direct masses). Source `results/pma_validation.csv`.

- 10 detections (SNR >= 3), all attributable to wide/outer companions —
  no swept inner planet's ceiling contradicted.
- 33 non-detections, **20 informative** (giant hosts, no face-on/heavy
  signature -> consistent with our ceilings). Low-mass-only non-detections
  are uninformative (undetectable at any inclination) and not counted.

## 2026-07-23 — mutual-inclination limit catalogue (`scripts/run_mutinc_limits.py`)

53 unflagged systems, planets held at edge-on masses, sigma_mut 0-40 deg,
1e5 orbits, 20 draws. Source `results/mutinc_limits.{csv,png}`.

- **21 systems have a mutual-inclination ceiling** sigma_max `15-40 deg`
  (median 30); 32 tolerate >= 40 deg; none fragile coplanar.
- Tightest (near-coplanar required): HD 184010 `15`, HD 191939 `20`,
  47 UMa / HD 27894 `25`.
- Conservative: 1e5 depth, deeper integration can only lower sigma_max.
- N-body counterpart to Volpi+2019's secular bounds on ten systems.

## Combined tallies (as of 2026-07-23)

- Constrained planets: `123` (main) + `21` (resonant) = **`144`**.
- Flagged systems: `3` (main) + `13` (resonant) = **`16`**.
- New catalogue product: `21` mutual-inclination limits.
- External validation: 4 direct masses (Feng) + 43-host PMA cross-check
  (Kervella), all consistent.
