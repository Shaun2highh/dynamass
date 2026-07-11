"""Data model for a planetary system as constrained by radial velocities."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

MSUN_PER_MJUP = 1.0 / 1047.57
MJUP_PER_MEARTH = 1.0 / 317.83
DAYS_PER_YEAR = 365.25


@dataclass
class Planet:
    name: str
    period_days: float
    msini_mjup: float
    ecc: float = 0.0
    # Longitude of periastron from the catalog; NaN means unknown.
    lper_deg: float = float("nan")
    transiting: bool = False
    mass_is_msini: bool = True
    # Symmetrized 1-sigma catalog uncertainties; NaN means unreported.
    period_err_days: float = float("nan")
    msini_err_mjup: float = float("nan")
    ecc_err: float = float("nan")
    lper_err_deg: float = float("nan")
    # Orbital phase at REF_EPOCH_JD, derived from the time of periastron;
    # NaN means unknown (randomized per draw). Needed for resonant systems.
    mean_anom_deg: float = float("nan")

    @property
    def period_yr(self) -> float:
        return self.period_days / DAYS_PER_YEAR

    @property
    def swept(self) -> bool:
        """Does this planet's mass scale as 1/sin(i) in the sweep?

        Transiting planets (known i ~ 90 deg) and astrometric/TTV true masses
        keep their catalog mass regardless of the sweep.
        """
        return self.mass_is_msini and not self.transiting

    def true_mass_mjup(self, mass_factor: float) -> float:
        """True mass when the orbit is tilted so that m = msini * mass_factor."""
        if not self.swept:
            return self.msini_mjup
        return self.msini_mjup * mass_factor


@dataclass
class System:
    name: str
    star_mass_msun: float
    planets: list[Planet] = field(default_factory=list)
    star_mass_err_msun: float = float("nan")
    # Which published fit the parameters came from ("" = pscomppars composite).
    ref: str = ""

    def sorted_planets(self) -> list[Planet]:
        return sorted(self.planets, key=lambda p: p.period_days)

    @property
    def min_period_yr(self) -> float:
        return min(p.period_yr for p in self.planets)


def mass_factor_to_inclination_deg(mass_factor: float) -> float:
    return math.degrees(math.asin(min(1.0, 1.0 / mass_factor)))


def inclination_deg_to_mass_factor(inc_deg: float) -> float:
    return 1.0 / math.sin(math.radians(inc_deg))


def semi_major_axis_au(period_yr: float, mstar_msun: float) -> float:
    """Kepler III in solar units (Msun, yr, AU)."""
    return (mstar_msun * period_yr**2) ** (1.0 / 3.0)


def hill_radius_au(a_au: float, m_msun: float, mstar_msun: float) -> float:
    return a_au * (m_msun / (3.0 * (mstar_msun + m_msun))) ** (1.0 / 3.0)


def mutual_hill_radius_au(
    a1_au: float, a2_au: float, m1_msun: float, m2_msun: float, mstar_msun: float
) -> float:
    return ((m1_msun + m2_msun) / (3.0 * mstar_msun)) ** (1.0 / 3.0) * (a1_au + a2_au) / 2.0
