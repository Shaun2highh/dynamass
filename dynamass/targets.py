"""Target selection against the NASA Exoplanet Archive (pscomppars table)."""

from __future__ import annotations

import io
import math
import re
import time

import pandas as pd
import requests

from .system import (
    MSUN_PER_MJUP,
    Planet,
    System,
    mutual_hill_radius_au,
    semi_major_axis_au,
)

TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
COLUMNS = (
    "hostname,pl_name,pl_orbper,pl_bmassj,pl_bmassprov,pl_orbeccen,"
    "pl_orblper,st_mass,tran_flag,discoverymethod,sy_pnum,"
    "pl_orbpererr1,pl_orbpererr2,pl_bmassjerr1,pl_bmassjerr2,"
    "pl_orbeccenerr1,pl_orbeccenerr2,pl_orblpererr1,pl_orblpererr2,"
    "pl_orbtper,st_masserr1,st_masserr2"
)


def _sym_err(row: pd.Series, base: str) -> float:
    """Symmetrized 1-sigma error from the archive's +/- columns."""
    errs = [abs(row[f"{base}err{i}"]) for i in (1, 2) if pd.notna(row[f"{base}err{i}"])]
    return float(sum(errs) / len(errs)) if errs else float("nan")


def _query(adql: str, timeout: int = 120, retries: int = 4) -> pd.DataFrame:
    # Parallel survey workers hit the TAP service hard; back off on failure.
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(
                TAP_URL, params={"query": adql, "format": "csv"}, timeout=timeout
            )
            resp.raise_for_status()
            return pd.read_csv(io.StringIO(resp.text))
        except Exception as exc:
            last_exc = exc
            time.sleep(2.0 * 2**attempt)
    raise last_exc


def _row_to_planet(row: pd.Series, epoch_jd: float) -> Planet:
    # epoch_jd = NaN disables phase derivation (mean_anom stays NaN -> random).
    ecc = row["pl_orbeccen"]
    lper = row["pl_orblper"]
    tper = row["pl_orbtper"]
    if pd.notna(tper) and pd.notna(epoch_jd):
        # Orbital phase at the system's common epoch, from the time of periastron.
        mean_anom = ((epoch_jd - float(tper)) / float(row["pl_orbper"]) * 360.0) % 360.0
    else:
        mean_anom = float("nan")
    return Planet(
        name=row["pl_name"],
        period_days=float(row["pl_orbper"]),
        msini_mjup=float(row["pl_bmassj"]),
        ecc=0.0 if pd.isna(ecc) else float(ecc),
        lper_deg=float("nan") if pd.isna(lper) else float(lper),
        transiting=bool(row["tran_flag"]),
        mass_is_msini=str(row["pl_bmassprov"]).startswith("Msini"),
        period_err_days=_sym_err(row, "pl_orbper"),
        msini_err_mjup=_sym_err(row, "pl_bmassj"),
        ecc_err=_sym_err(row, "pl_orbeccen"),
        lper_err_deg=_sym_err(row, "pl_orblper"),
        mean_anom_deg=mean_anom,
    )


def _rows_to_system(hostname: str, rows: pd.DataFrame, derive_phases: bool = False) -> System:
    # Phases are derived only for single-reference fits: pscomppars composites
    # mix incompatible fits, so their periastron times are mutually meaningless
    # (this false phase coherence broke near-resonant systems in v1 tests).
    # The common epoch sits near the fit's own epochs to keep the lever arm of
    # period uncertainty on the derived mean anomalies short. Identical tper
    # across planets means the archive stored the fit epoch there, not real
    # periastron times (seen for GJ 876/Rivera 2010) — phases are unknowable.
    tpers = rows["pl_orbtper"].dropna()
    degenerate = len(rows) > 1 and tpers.nunique() == 1
    usable = derive_phases and len(tpers) and not degenerate
    epoch_jd = float(tpers.median()) if usable else float("nan")
    planets = [_row_to_planet(r, epoch_jd) for _, r in rows.iterrows()]
    star_rows = rows[rows["st_mass"].notna()]
    return System(
        name=hostname,
        star_mass_msun=float(star_rows["st_mass"].iloc[0]),
        planets=planets,
        star_mass_err_msun=_sym_err(star_rows.iloc[0], "st_mass"),
    )


def fetch_system(hostname: str, allow_fallback: bool = False) -> System:
    """Fetch one system by host star name, e.g. 'HD 12661'.

    With allow_fallback, a failed fetch falls back to bundled literature
    values when the host is in FALLBACKS (offline use).
    """
    try:
        escaped = hostname.replace("'", "''")
        adql = f"select {COLUMNS} from pscomppars where hostname='{escaped}'"
        df = _query(adql)
        if df.empty:
            raise ValueError(f"No planets found for host {hostname!r}")
    except Exception:
        if allow_fallback and hostname in FALLBACKS:
            return FALLBACKS[hostname]()
        raise
    df = df.dropna(subset=["pl_orbper", "pl_bmassj"])
    return _rows_to_system(hostname, df)


def fetch_system_single_ref(hostname: str, refname: str | None = None) -> System:
    """Fetch one system from a single self-consistent published fit (ps table).

    pscomppars stitches each parameter from possibly different papers, which
    destroys phase-coherent configurations (fatal for resonant systems). This
    pulls all planets from one reference: the given refname, or the newest
    reference that covers every planet with period, mass, eccentricity, and
    time of periastron.
    """
    escaped = hostname.replace("'", "''")
    adql = f"select {COLUMNS},pl_refname from ps where hostname='{escaped}'"
    df = _query(adql)
    if df.empty:
        raise ValueError(f"No ps rows for host {hostname!r}")
    n_planets = df["pl_name"].nunique()

    def year(ref: str) -> int:
        m = re.search(r"(19|20)\d{2}", str(ref))
        return int(m.group(0)) if m else 0

    candidates = []
    for ref, rows in df.groupby("pl_refname"):
        rows = rows.drop_duplicates(subset="pl_name")
        complete = (
            rows["pl_name"].nunique() == n_planets
            and rows[["pl_orbper", "pl_bmassj", "pl_orbeccen", "pl_orbtper"]].notna().all().all()
            and rows["st_mass"].notna().any()
        )
        if complete:
            candidates.append((year(str(ref)), str(ref), rows))
    if refname is not None:
        matches = [c for c in candidates if refname.lower() in c[1].lower()]
        if not matches:
            raise ValueError(f"No complete single-reference set matching {refname!r}")
        _, ref, rows = matches[0]
    elif candidates:
        _, ref, rows = max(candidates, key=lambda c: c[0])
    else:
        raise ValueError(f"No single reference covers all planets of {hostname!r}")
    system = _rows_to_system(hostname, rows, derive_phases=True)
    inner = re.search(r">([^<]+)<", ref)  # pl_refname is an HTML anchor
    system.ref = inner.group(1).strip() if inner else ref
    return system


def fetch_qualifying_systems(
    min_planets: int = 2,
    max_adjacent_period_ratio: float = 6.0,
) -> list[System]:
    """All systems that qualify for the survey.

    Qualifies if: every planet has a period and a mass; the star mass is known;
    at least one planet is a non-transiting Msini detection; and at least one
    adjacent pair is packed tightly enough (period ratio below the cut) for
    dynamical interactions to bite on survey timescales.
    """
    adql = f"select {COLUMNS} from pscomppars where sy_pnum>={min_planets}"
    df = _query(adql)
    systems: list[System] = []
    for hostname, rows in df.groupby("hostname"):
        if rows["pl_orbper"].isna().any() or rows["pl_bmassj"].isna().any():
            continue
        if rows["st_mass"].dropna().empty:
            continue
        sys = _rows_to_system(str(hostname), rows)
        if len(sys.planets) < min_planets:
            continue
        swept = [p for p in sys.planets if p.mass_is_msini and not p.transiting]
        if not swept:
            continue
        periods = [p.period_days for p in sys.sorted_planets()]
        ratios = [b / a for a, b in zip(periods, periods[1:])]
        if min(ratios) > max_adjacent_period_ratio:
            continue
        systems.append(sys)
    return systems


def fallback_hd12661() -> System:
    """Literature values for HD 12661 (two giant planets), used when offline."""
    return System(
        name="HD 12661",
        star_mass_msun=1.14,
        planets=[
            Planet("HD 12661 b", period_days=262.71, msini_mjup=2.30, ecc=0.377, lper_deg=296.0),
            Planet("HD 12661 c", period_days=1708.0, msini_mjup=1.92, ecc=0.031, lper_deg=165.0),
        ],
    )


FALLBACKS = {"HD 12661": fallback_hd12661}

CRIT_DELTA = 2.0 * math.sqrt(3.0)


def pair_metrics(system: System) -> tuple[float, str, float]:
    """(f_crit, pair_label, delta_at_1x) for the most fragile adjacent pair.

    For each adjacent pair, the separation in mutual Hill radii shrinks as the
    swept mass factor f grows (R_H ~ f^(1/3)). f_crit is the factor at which
    the pair reaches the two-planet overlap criterion Delta = 2*sqrt(3)
    (Gladman 1993); multi-planet systems generally destabilize at wider
    spacings, so f_crit is a conservative pre-estimate of the dynamical
    ceiling.
    """
    best = (math.inf, "", math.inf)
    planets = system.sorted_planets()
    for p1, p2 in zip(planets, planets[1:]):
        a1 = semi_major_axis_au(p1.period_yr, system.star_mass_msun)
        a2 = semi_major_axis_au(p2.period_yr, system.star_mass_msun)
        m1 = p1.msini_mjup * MSUN_PER_MJUP
        m2 = p2.msini_mjup * MSUN_PER_MJUP
        rh = mutual_hill_radius_au(a1, a2, m1, m2, system.star_mass_msun)
        delta = (a2 - a1) / rh
        # Eccentric orbits approach closer than circular spacing suggests.
        delta_ecc = (a2 * (1 - p2.ecc) - a1 * (1 + p1.ecc)) / rh
        delta_eff = max(min(delta, delta_ecc), 0.0)
        scale = 1.0 if (p1.swept and p2.swept) else 0.5  # only part of the pair mass grows
        if delta_eff <= 0:
            f_crit = 1.0
        else:
            f_crit = max(1.0, (delta_eff / CRIT_DELTA) ** 3 / scale)
        if f_crit < best[0]:
            best = (f_crit, f"{p1.name} / {p2.name}", delta_eff)
    return best
