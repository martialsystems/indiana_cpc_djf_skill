# Copyright (c) 2026 Martial Systems LLC
"""GHCND daily TAVG and PRCP. SNOW cannot substitute for PRCP. TMIN-only cannot substitute for TAVG."""

from __future__ import annotations

import csv
import gzip
import io
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Callable

import numpy as np

from cpcskill.config import (
    COMPLETE_FRAC,
    CORE_STATIONS,
    GHCND_STATION_URL,
    GHCND_STATIONS_URL,
    MIN_TRAIN_WINTERS,
    MM_PER_INCH,
)
from cpcskill.errors import FetchError
from cpcskill.http import get_bytes
from cpcskill.labels import complete_enough, djf_ndays, winter_id_of
from cpcskill.split import TRAIN, role


def parse_station_line(line: str) -> dict[str, Any] | None:
    if len(line) < 41:
        return None
    sid = line[0:11].strip()
    try:
        lat = float(line[12:20])
        lon = float(line[21:30])
        elev = float(line[31:37])
    except ValueError:
        return None
    name = line[41:71].strip() if len(line) >= 71 else sid
    return {"station_id": sid, "lat": lat, "lon": lon, "elev_m": elev, "name": name}


def load_station_inventory(cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> dict[str, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "ghcnd-stations.txt"
    if not path.is_file() or path.stat().st_size == 0:
        path.write_bytes(getter(GHCND_STATIONS_URL))
    text = path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        rec = parse_station_line(line)
        if rec:
            out[rec["station_id"]] = rec
    if not out:
        raise FetchError("empty GHCND station inventory")
    return out


def parse_daily(text: str) -> list[tuple[date, str, float]]:
    rows: list[tuple[date, str, float]] = []
    for rec in csv.reader(io.StringIO(text)):
        if len(rec) < 4:
            continue
        elem = rec[2].strip()
        if elem not in {"PRCP", "TAVG", "TMAX", "TMIN"}:
            continue
        qflag = rec[5].strip() if len(rec) > 5 else ""
        if qflag:
            continue
        try:
            raw = int(rec[3])
        except ValueError:
            continue
        if raw == -9999:
            continue
        day = date.fromisoformat(f"{rec[1][0:4]}-{rec[1][4:6]}-{rec[1][6:8]}")
        rows.append((day, elem, float(raw)))
    return rows


def _to_native(elem: str, raw: float) -> float:
    if elem == "PRCP":
        return (raw / 10.0) / MM_PER_INCH
    if elem in {"TAVG", "TMAX", "TMIN"}:
        return raw / 10.0
    return raw


def load_station_csv(sid: str, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> list[tuple[date, str, float]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{sid}.csv.gz"
    if not path.is_file() or path.stat().st_size == 0:
        body = getter(GHCND_STATION_URL.format(sid=sid))
        if not body:
            raise FetchError(f"empty GHCND {sid}")
        path.write_bytes(body)
    raw = gzip.decompress(path.read_bytes()).decode("utf-8", errors="replace")
    days = parse_daily(raw)
    if not days:
        raise FetchError(f"GHCND {sid} has no TAVG/PRCP/TMAX/TMIN")
    return days


def assemble_winters(daily: dict[str, list[tuple[date, str, float]]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, int], dict[str, Any]] = {}
    for sid, rows in daily.items():
        for day, elem, raw in rows:
            if day.month not in {12, 1, 2}:
                continue
            wid = winter_id_of(day)
            b = buckets.setdefault(
                (sid, wid),
                {"tavg": [], "tmax": [], "tmin": [], "prcp": [], "n_tavg": 0, "n_prcp": 0},
            )
            val = _to_native(elem, raw)
            if elem == "TAVG":
                b["tavg"].append(val)
                b["n_tavg"] += 1
            elif elem == "TMAX":
                b["tmax"].append((day, val))
            elif elem == "TMIN":
                b["tmin"].append((day, val))
            elif elem == "PRCP":
                b["prcp"].append(val)
                b["n_prcp"] += 1

    out: list[dict[str, Any]] = []
    for (sid, wid) in sorted(buckets):
        rec = buckets[(sid, wid)]
        tavg = list(rec["tavg"])
        if not tavg:
            tmax = {d: v for d, v in rec["tmax"]}
            tmin = {d: v for d, v in rec["tmin"]}
            shared = sorted(set(tmax) & set(tmin))
            tavg = [0.5 * (tmax[d] + tmin[d]) for d in shared]
            rec["n_tavg"] = len(tavg)
        t_ok = complete_enough(int(rec["n_tavg"]), int(wid), floor=COMPLETE_FRAC)
        p_ok = complete_enough(int(rec["n_prcp"]), int(wid), floor=COMPLETE_FRAC)
        if not t_ok or not p_ok:
            continue
        ndays = float(djf_ndays(int(wid)))
        out.append(
            {
                "station_id": sid,
                "winter_id": int(wid),
                "tavg_c": float(np.mean(tavg)),
                "prcp_in": float(np.sum(rec["prcp"])),
                "tavg_frac": float(rec["n_tavg"]) / ndays,
                "prcp_frac": float(rec["n_prcp"]) / ndays,
            }
        )
    return out


def require_core_train_floor(rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        if role(int(r["winter_id"])) == TRAIN:
            counts[r["station_id"]] += 1
    for sid, _ in CORE_STATIONS:
        if counts.get(sid, 0) < MIN_TRAIN_WINTERS:
            raise FetchError(f"core {sid} TAVG/PRCP too thin for terciles: train n={counts.get(sid, 0)}")
    missing = {sid for sid, _ in CORE_STATIONS} - set(counts)
    if missing:
        raise FetchError(f"required cores missing after QC: {sorted(missing)}")

