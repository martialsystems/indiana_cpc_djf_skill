# Copyright (c) 2026 Martial Systems LLC
"""Two figures: holdout Brier bars, north vs south temperature."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from cpcskill.claims import require_clean
from cpcskill.config import (
    CORE_STATIONS,
    FIXTURE_BARS_SUBTITLE,
    FIXTURE_NORTH_SUBTITLE,
    LIVE_BARS_SUBTITLE,
    LIVE_NORTH_SUBTITLE,
    MAX_FIGURES,
    NORTH_IDS,
    PRCP,
    SOUTH_IDS,
    TAVG,
)
from cpcskill.errors import FigureCapError


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def _brier(block: dict[str, Any], who: str) -> float:
    val = (block.get(who) or {}).get("brier")
    return float("nan") if val is None else float(val)


def write_bars(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    hold = fit["holdout"]
    labels = ["equal chance", "CPC", "last year"]
    x = np.arange(len(labels), dtype=float)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.8), sharey=True)
    for ax, var, heading in zip(axes, (TAVG, PRCP), ("Temperature", "Precipitation")):
        vals = [_brier(hold[var], "ec"), _brier(hold[var], "cpc"), _brier(hold[var], "last_year")]
        colors = ["#64748b", "#1d4ed8", "#b45309"]
        ax.bar(x, vals, color=colors)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=20, ha="right")
        ax.set_title(heading, fontsize=10)
        ax.set_ylabel("Brier")
        ax.axhline(hold[var]["ec"]["brier"], color="#0f172a", lw=0.8, ls=":")
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.24, top=0.86, wspace=0.18)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_north_south(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = []
    cpc = []
    ec = []
    for sid, city in CORE_STATIONS:
        block = (fit.get("by_station") or {}).get(sid) or {}
        t = block.get(TAVG) or {}
        names.append(city)
        cpc.append(_brier(t, "cpc"))
        ec.append(_brier(t, "ec"))
    x = np.arange(len(names), dtype=float)
    width = 0.35
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    ax.bar(x - width / 2, ec, width, color="#64748b", label="equal chance")
    ax.bar(x + width / 2, cpc, width, color="#1d4ed8", label="CPC")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8, rotation=28, ha="right")
    ax.set_ylabel("Temperature Brier")
    ax.legend(fontsize=7, loc="upper right")
    north = " / ".join(city for sid, city in CORE_STATIONS if sid in NORTH_IDS)
    south = " / ".join(city for sid, city in CORE_STATIONS if sid in SOUTH_IDS)
    ax.set_title(f"North {north}; south {south}", fontsize=10)
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.28, top=0.86)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(2)
    log_dir.mkdir(parents=True, exist_ok=True)
    bars = write_bars(
        log_dir / "skill_bars.png",
        fit=fit,
        title="Holdout CPC vs climatology",
        subtitle=LIVE_BARS_SUBTITLE if live else FIXTURE_BARS_SUBTITLE,
    )
    north = write_north_south(
        log_dir / "north_south.png",
        fit=fit,
        title="Holdout temperature north vs south",
        subtitle=LIVE_NORTH_SUBTITLE if live else FIXTURE_NORTH_SUBTITLE,
    )
    paths = [bars, north]
    _cap(len(paths))
    return [p.name for p in paths]
