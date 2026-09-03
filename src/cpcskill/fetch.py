# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND + frozen CPC subset. Empty core stops. Live lead-4 URL refused."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from cpcskill.config import CORE_IDS, CORE_STATIONS, REPO_ROOT
from cpcskill.cpc_archive import load_subset
from cpcskill.errors import ArchiveError, FetchError
from cpcskill.ghcnd import assemble_winters, load_station_csv, load_station_inventory, require_core_train_floor
from cpcskill.http import get_bytes
from cpcskill.pack import SeasonPack


def _subset_path(cache_dir: Path) -> Path:
    locked = REPO_ROOT / "data" / "raw" / "cpc" / "august_lead4.json"
    cached = cache_dir / "cpc" / "august_lead4.json"
    if locked.is_file():
        return locked
    if cached.is_file():
        return cached
    raise ArchiveError("missing frozen CPC August lead-4 subset data/raw/cpc/august_lead4.json")


def fetch_live(*, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> tuple[SeasonPack, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    inventory = load_station_inventory(cache_dir, getter=getter)
    daily: dict[str, list] = {}
    for sid, _ in CORE_STATIONS:
        try:
            daily[sid] = load_station_csv(sid, cache_dir, getter=getter)
        except FetchError:
            raise FetchError(f"empty GHCND TAVG/PRCP for required core {sid}") from None
        elems = {e for _, e, _ in daily[sid]}
        if "PRCP" not in elems:
            raise FetchError(f"SNOW cannot substitute for PRCP at {sid}")
        if "TAVG" not in elems and not ({"TMAX", "TMIN"} <= elems):
            raise FetchError(f"TMIN-only cannot substitute for TAVG at {sid}")

    winters = assemble_winters(daily)
    require_core_train_floor(winters)
    missing_cores = set(CORE_IDS) - {r["station_id"] for r in winters}
    if missing_cores:
        raise FetchError(f"required cores missing after QC: {sorted(missing_cores)}")

    probs = load_subset(_subset_path(cache_dir))
    rows: list[dict[str, Any]] = []
    n_dropped_cpc = 0
    for rec in winters:
        sid = rec["station_id"]
        wid = int(rec["winter_id"])
        pt = probs.get((sid, wid, "tavg"))
        pp = probs.get((sid, wid, "prcp"))
        if pt is None or pp is None:
            n_dropped_cpc += 1
            pt = np.full(3, np.nan)
            pp = np.full(3, np.nan)
        meta = inventory.get(sid) or {}
        rows.append(
            {
                **rec,
                "name": next(n for s, n in CORE_STATIONS if s == sid),
                "lat": float(meta.get("lat") or 0.0),
                "lon": float(meta.get("lon") or 0.0),
                "p_tavg": pt,
                "p_prcp": pp,
            }
        )
    if not rows:
        raise FetchError("no complete station-winters after CPC join")
    still_missing = set(CORE_IDS) - {r["station_id"] for r in rows}
    if still_missing:
        raise FetchError(f"required cores missing after CPC join: {sorted(still_missing)}")

    pack = SeasonPack(
        station_id=np.array([r["station_id"] for r in rows], dtype=object),
        name=np.array([r["name"] for r in rows], dtype=object),
        winter_id=np.array([r["winter_id"] for r in rows], dtype=int),
        tavg_c=np.array([r["tavg_c"] for r in rows], dtype=float),
        prcp_in=np.array([r["prcp_in"] for r in rows], dtype=float),
        tavg_frac=np.array([r["tavg_frac"] for r in rows], dtype=float),
        prcp_frac=np.array([r["prcp_frac"] for r in rows], dtype=float),
        p_tavg=np.vstack([r["p_tavg"] for r in rows]),
        p_prcp=np.vstack([r["p_prcp"] for r in rows]),
        source="live",
        extra={"n_dropped_cpc": n_dropped_cpc, "n_dropped_incomplete": 0, "element": "TAVG+PRCP", "contestant": "cpc"},
    )
    meta = {
        "n_stations": pack.n_stations,
        "n_rows": pack.n_rows,
        "product": "GHCND TAVG/PRCP + CPC August lead 4",
        "n_dropped_cpc": n_dropped_cpc,
        "cache_dir": str(cache_dir),
        "cpc_subset": str(_subset_path(cache_dir)),
    }
    return pack, meta
