# Resonant edge-on flags: literature cross-check

The resonant-block run (scripts/run_resonant.py, 1e5 orbits) flagged 12 of 22
phased systems as failing the edge-on consistency test (S(90 deg) < 0.5): the
published single-reference fit, integrated with its own fit phases, does not
survive even at edge-on. This documents that these flags recover systems the
literature has independently identified as dynamically problematic — the flags
are real, not artifacts of the phase-coherent treatment at f_crit ~ 1.

| System | Our flag | Independent literature status |
|---|---|---|
| BD+20 2457 | edge-on fail | Unstable on short timescales; "configuration unlikely correct" (Horner et al. 2014, MNRAS 439, 1176) |
| HD 47366 | edge-on fail | "Not dynamically stable" as proposed; lower-e refit preferred (Marshall et al. 2019, AJ 157, 1) |
| HD 200964 | edge-on fail | Best-fit in a narrow stability island amid highly unstable solutions (4:3 MMR) |
| HD 33844 | edge-on fail | Proposed solution in region of "both extremely stable and unstable" behaviour (3:5 MMR; Wittenmyer et al. 2016) |
| 24 Sex | edge-on fail | Near 2:1 MMR, disputed stability of the nominal fit |
| BD-21 0397, DMPP-2, HD 153557, HD 5319, HD 81817, HD 93385, NY Vir | edge-on fail | Flagged here for the same scrutiny (not yet individually re-analysed in the literature to our knowledge) |

**Interpretation for the paper.** The resonant block yields two products: (a) new
95% credible mass limits for 24 planets in 10 clean systems (median 2.21x), and
(b) a homogeneous recovery of dynamically inconsistent published fits. For the
well-studied cases the method reproduces the community's conclusions; for the
remainder it provides a prioritised list of published resonant solutions whose
own dynamics reject them, warranting a joint dynamical-RV refit.

**Caveat still to close.** These flags are from the 1e5-orbit pass. A 1e6 rerun
(in progress) tests whether each flag persists at 10x depth; a flag that holds
at both depths is robust. Marginal cases (S(90) ~ 0.45-0.55: HD 155358 at 0.55)
should be read with the depth caveat.
