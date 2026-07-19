"""External validation (Part B): astrometric true masses vs our stability ceilings.

Our survey produces upper limits on true masses that the radial-velocity data
alone cannot provide. Where an independent true mass exists from Hipparcos-Gaia
astrometry, a valid upper limit must lie above it. We cross-match the survey
catalog against the combined RV + astrometry true masses of Feng et al. (2022,
ApJS 262, 21), which derive companion masses and inclinations from
proper-motion anomalies.

The overlap is intrinsically small: most of the surveyed planets are too
low-mass for current astrometry to weigh, which is the motivation for the
survey. Companions are matched to our planets by orbital period (within 5 per
cent); wide outer companions that the survey does not sweep are excluded.

Usage: python scripts/validate_astrometry.py
Writes results/astrometry_validation.csv.
"""

import io
import re
import pandas as pd
import requests

from dynamass.paths import results_dir

VIZIER = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"
ARCHIVE = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s)).upper().replace("_", "")


def main() -> None:
    cat = pd.read_csv(results_dir() / "survey_catalog_1e6_prod.csv")
    swept = cat[cat["swept"]].copy()

    feng = pd.read_csv(io.StringIO(requests.post(
        VIZIER,
        data={"request": "doQuery", "lang": "ADQL", "format": "csv",
              "query": 'select * from "J/ApJS/262/21/table3"'},
        timeout=180).text))
    ours = {norm(h): h for h in cat["system"].unique()}
    feng["sys"] = feng["Host"].map(norm).map(ours)
    hits = feng[feng["sys"].notna() & feng["mc"].notna()].copy()

    # Periods for the matched systems (not stored in the catalog).
    syslist = ",".join("'%s'" % s.replace("'", "''") for s in hits["sys"].unique())
    per = pd.read_csv(io.StringIO(requests.get(ARCHIVE, params={
        "query": f"select pl_name,hostname,pl_orbper from pscomppars "
                 f"where hostname in ({syslist})",
        "format": "csv"}, timeout=120).text))

    rows = []
    for _, f in hits.iterrows():
        op = per[per["hostname"] == f["sys"]].copy()
        if op.empty:
            continue
        op["dP"] = (op["pl_orbper"] - f["Per-d"]).abs() / f["Per-d"]
        m = op.sort_values("dP").iloc[0]
        if m["dP"] > 0.05:  # no period match: not the same planet
            continue
        r = swept[(swept["system"] == f["sys"]) & (swept["planet"] == m["pl_name"])]
        if r.empty:  # matched planet is not in our swept set (fixed / transiting)
            continue
        m95 = float(r["mass_95_mjup"].iloc[0])
        rows.append(dict(
            planet=m["pl_name"], period_d=round(float(f["Per-d"]), 2),
            msini_mjup=round(float(r["msini_mjup"].iloc[0]), 3),
            m_astrometric_mjup=round(float(f["mc"]), 3),
            i_astrometric_deg=None if pd.isna(f["i"]) else round(float(f["i"]), 1),
            our_ceiling_mjup=round(m95, 3),
            consistent=bool(f["mc"] <= m95)))

    out = pd.DataFrame(rows).sort_values("period_d")
    out.to_csv(results_dir() / "astrometry_validation.csv", index=False)
    n = len(out)
    ok = int(out["consistent"].sum()) if n else 0
    print(f"{n} constrained planets have an independent astrometric true mass "
          f"(Feng et al. 2022).")
    print(f"{ok}/{n} fall below our 95% stability ceiling.\n")
    if n:
        print(out.to_string(index=False))
    print(f"\nWrote {results_dir() / 'astrometry_validation.csv'}")


if __name__ == "__main__":
    main()
