"""Output-path conventions shared by every runner script."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slug(name: str) -> str:
    return name.replace(" ", "_").replace("'", "").lower()


def depth_tag(n_orbits: float) -> str:
    """Filename suffix for a survey depth; the default depth (1e5) has none."""
    if n_orbits == 1e5:
        return ""
    return "_" + f"{n_orbits:.0e}".replace("+0", "").replace("+", "")


def results_dir(subdir: str = "") -> Path:
    path = ROOT / "results" / subdir if subdir else ROOT / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path
