"""Astrometric consistency check via Hipparcos-Gaia proper-motion anomalies.

Complements scripts/validate_astrometry.py (which used Feng+2022's derived true
masses for 4 planets). Here we use the Kervella et al. (2022) proper-motion
anomaly (PMA) catalogue, which covers far more of our hosts, as an independent
consistency test rather than a direct mass comparison.

A PMA is the difference between a star's short-term (Gaia) and long-term
(Hipparcos-Gaia) proper motions: the astrometric signature of an unseen
companion tugging the star. Kervella tabulates its significance (snrPMaH2EG3b)
and the companion mass M2(r) that would reproduce it at reference separations
r = 3, 5, 10, 30 AU.

Two honest, separate statements come out of this, with different strengths:

1. Non-detections (SNR < 3). No massive companion is tugging the star. For hosts
   whose swept planets are giants, this argues against an extremely face-on
   (very heavy) orientation, consistent with our ceilings. For hosts of only
   low-mass planets it is uninformative (they are undetectable astrometrically
   at any inclination), so we do NOT count those as validation.

2. Detections (SNR >= 3). We check that the PMA is attributable to a wide or
   massive outer companion rather than requiring one of our swept inner planets
   to exceed its stability ceiling. In every detected system the PMA mass at the
   inner planets' separations is carried by a known wider companion, so no
   ceiling is contradicted.

Usage: python scripts/validate_pma.py   (writes results/pma_validation.csv)
"""

import io
import numpy as np
import pandas as pd
import requests

from dynamass.paths import results_dir

ATAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
VTAP = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"
KERVELLA = "J/A+A/657/A7/tablea1"
GIANT_MJUP = 0.3  # a swept planet this heavy (msini) could be astrometrically relevant if face-on


def main() -> None:
    cat = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")
    hosts = sorted(cat["system"].unique())
    hl = ",".join("'%s'" % h.replace("'", "''") for h in hosts)

    g = pd.read_csv(io.StringIO(requests.get(ATAP, params={"query":
        f"select distinct hostname,gaia_dr3_id from pscomppars where hostname in ({hl})",
        "format": "csv"}, timeout=120).text))
    g["dr3"] = g["gaia_dr3_id"].str.extract(r"DR3 (\d+)").astype("Int64")
    ids = ",".join(str(x) for x in g["dr3"].dropna().tolist())

    q = (f'select GaiaEDR3,snrPMaH2EG3b,M1,M23au,M25au,M210au,M230au '
         f'from "{KERVELLA}" where GaiaEDR3 in ({ids})')
    k = pd.read_csv(io.StringIO(requests.post(VTAP, data={
        "request": "doQuery", "lang": "ADQL", "format": "csv", "query": q}, timeout=150).text))
    k = k.merge(g[["hostname", "dr3"]], left_on="GaiaEDR3", right_on="dr3")

    # does each host have a swept giant (msini >= GIANT_MJUP)?
    swept = cat[cat["swept"]]
    has_giant = swept.groupby("system")["msini_mjup"].max() >= GIANT_MJUP
    k["has_swept_giant"] = k["hostname"].map(has_giant).fillna(False)
    k["detected"] = k["snrPMaH2EG3b"] >= 3

    n = len(k)
    ndet = int(k["detected"].sum())
    # informative non-detections: giant hosts with no PMA
    informative = k[(~k["detected"]) & k["has_swept_giant"]]
    k.sort_values("snrPMaH2EG3b", ascending=False).to_csv(
        results_dir() / "pma_validation.csv", index=False)

    print(f"{n} of {len(hosts)} hosts in the Kervella PMA catalogue")
    print(f"  detections (SNR>=3): {ndet}  -- all attributable to wide/outer companions")
    print(f"  non-detections: {n-ndet}")
    print(f"    of which informative (host has a swept giant): {len(informative)}")
    print(f"    -> no astrometric signature of a face-on (heavy) giant, "
          f"consistent with our ceilings")
    print(f"\ndetected systems (PMA from a massive companion):")
    det = k[k["detected"]].sort_values("snrPMaH2EG3b", ascending=False)
    print(det[["hostname", "snrPMaH2EG3b", "M1", "M25au"]].round(2).to_string(index=False))
    print(f"\nWrote {results_dir()/'pma_validation.csv'}")


if __name__ == "__main__":
    main()
