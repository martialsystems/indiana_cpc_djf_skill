# Copyright (c) 2026 Martial Systems LLC
"""Issued CPC tercile probabilities. ASCII archive, not the live lead-4 GIF."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Callable

import numpy as np

_Z_TERCILE = 0.43072729929545744  # Φ^{-1}(2/3)

from cpcskill.config import (
    CPC_FDF_PRCP,
    CPC_FDF_TEMP,
    CPC_LEAD,
    FDF_ISSUE_YEARS,
    ISSUE_MONTH,
    LIVE_LEAD4_PRCP,
    LIVE_LEAD4_TEMP,
    N_FORECAST_DIVISIONS,
    STATION_CD,
)
from cpcskill.errors import ArchiveError
from cpcskill.http import get_bytes

_HEADER = 5
_HDR = re.compile(r"^\s*(19|20)\d{2}\s+\d{1,2}\s+\d{1,2}\s+102\s+\d+\s*$")


def _forbid_live_url(source: str) -> None:
    text = source.lower()
    for banned in (LIVE_LEAD4_TEMP, LIVE_LEAD4_PRCP, "lead04/off04"):
        if banned.lower() in text:
            raise ArchiveError(f"live lead-4 URL is not the science lock: {source}")


def _split_glued_negatives(text: str) -> str:
    return re.sub(r"(?<=[\d.])-(?=\d)", " -", text)


def _probs_from_body(body: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = N_FORECAST_DIVISIONS
    if body.size == 2 * n:
        below = body[:n]
        above = body[n:]
        near = 1.0 - below - above
        near = np.clip(near, 0.0, 1.0)
        return below, near, above
    if body.size == 3 * n:
        return body[:n], body[n : 2 * n], body[2 * n :]
    raise ArchiveError(f"CPC body has {body.size} values, expected {2 * n} or {3 * n}")


def parse_cpcllf(text: str) -> list[dict[str, Any]]:
    text = _split_glued_negatives(text)
    lines = text.splitlines()
    hdr_idx = [i for i, line in enumerate(lines) if _HDR.match(line)]
    if not hdr_idx:
        # Fixture strings are one whitespace blob.
        tokens = text.split()
        recs: list[dict[str, Any]] = []
        i = 0
        ntok = len(tokens)
        while i + _HEADER + 2 * N_FORECAST_DIVISIONS <= ntok:
            try:
                year = int(float(tokens[i]))
                month = int(float(tokens[i + 1]))
                lead = int(float(tokens[i + 2]))
                nloc = int(float(tokens[i + 3]))
                kind = int(float(tokens[i + 4]))
            except ValueError:
                break
            if nloc != N_FORECAST_DIVISIONS or not (1990 <= year <= 2035):
                break
            take = 3 * N_FORECAST_DIVISIONS
            if i + _HEADER + take > ntok:
                take = 2 * N_FORECAST_DIVISIONS
            body = np.array([float(x) for x in tokens[i + _HEADER : i + _HEADER + take]], dtype=float)
            below, near, above = _probs_from_body(body)
            recs.append({"year": year, "month": month, "lead": lead, "kind": kind, "below": below, "near": near, "above": above})
            i += _HEADER + take
        if not recs:
            raise ArchiveError("no CPC records parsed")
        return recs

    recs = []
    for j, start in enumerate(hdr_idx):
        end = hdr_idx[j + 1] if j + 1 < len(hdr_idx) else len(lines)
        hdr = lines[start].split()
        year, month, lead, nloc, kind = (int(hdr[0]), int(hdr[1]), int(hdr[2]), int(hdr[3]), int(hdr[4]))
        if nloc != N_FORECAST_DIVISIONS:
            raise ArchiveError(f"expected {N_FORECAST_DIVISIONS} divisions, got {nloc}")
        body_toks = " ".join(lines[start + 1 : end]).split()
        body = np.array([float(x) for x in body_toks], dtype=float)
        below, near, above = _probs_from_body(body)
        recs.append({"year": year, "month": month, "lead": lead, "kind": kind, "below": below, "near": near, "above": above})
    if not recs:
        raise ArchiveError("no CPC records parsed")
    return recs



def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def gaussian_tercile_probs(fmean: float, fsd: float, cmean: float, csd: float) -> np.ndarray:
    """P(below, near, above) from CPC forecast vs climatology Gaussians."""
    if fsd <= 0 or csd <= 0:
        return np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=float)
    lo = cmean - _Z_TERCILE * csd
    hi = cmean + _Z_TERCILE * csd
    p_below = _phi((lo - fmean) / fsd)
    p_above = 1.0 - _phi((hi - fmean) / fsd)
    p_below = min(max(p_below, 0.0), 1.0)
    p_above = min(max(p_above, 0.0), 1.0)
    p_near = max(0.0, 1.0 - p_below - p_above)
    s = p_below + p_near + p_above
    if s <= 0:
        return np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=float)
    return np.array([p_below / s, p_near / s, p_above / s], dtype=float)


def parse_fdf(text: str, *, cds: set[int] | None = None) -> list[dict[str, Any]]:
    """Yearly CPC forecast-distribution file. Data rows: year mn lead cd r ... fmean cmean fsd csd [power]."""
    wanted = cds if cds is not None else set(STATION_CD.values())
    recs: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 22:
            continue
        try:
            year = int(parts[0])
            month = int(parts[1])
            lead = int(parts[2])
            cd = int(parts[3])
        except ValueError:
            continue
        if year < 1994 or month < 1 or month > 12 or lead < 1:
            continue
        if cd not in wanted:
            continue
        try:
            skill_r = float(parts[4])
            # 22 fields: ... fmean cmean fsd csd. 23 fields: power is last.
            if len(parts) >= 23:
                fmean, cmean, fsd, csd = (float(parts[-5]), float(parts[-4]), float(parts[-3]), float(parts[-2]))
            else:
                fmean, cmean, fsd, csd = (float(parts[-4]), float(parts[-3]), float(parts[-2]), float(parts[-1]))
        except ValueError:
            continue
        recs.append(
            {
                "year": year,
                "month": month,
                "lead": lead,
                "cd": cd,
                "r": skill_r,
                "fmean": fmean,
                "cmean": cmean,
                "fsd": fsd,
                "csd": csd,
                "p": gaussian_tercile_probs(fmean, fsd, cmean, csd),
            }
        )
    if not recs:
        raise ArchiveError("no FDF rows parsed")
    return recs


def extract_august_lead4(recs: list[dict[str, Any]]) -> dict[int, np.ndarray]:
    """winter_id (January year) -> (102, 3) probabilities."""
    out: dict[int, np.ndarray] = {}
    for rec in recs:
        if int(rec["month"]) != ISSUE_MONTH or int(rec["lead"]) != CPC_LEAD:
            continue
        winter_id = int(rec["year"]) + 1
        p = np.column_stack([rec["below"], rec["near"], rec["above"]])
        out[winter_id] = p
    return out


def station_probs(grid: np.ndarray, sid: str) -> np.ndarray:
    cd = STATION_CD[sid]
    idx = cd - 1
    if idx < 0 or idx >= N_FORECAST_DIVISIONS:
        raise ArchiveError(f"forecast division {cd} out of range")
    return np.asarray(grid[idx], dtype=float)


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def load_or_fetch(url: str, dest: Path, getter: Callable[[str], bytes] = get_bytes) -> bytes:
    _forbid_live_url(url)
    _forbid_live_url(str(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest.read_bytes()
    body = getter(url)
    dest.write_bytes(body)
    return body


def _fdf_august_lead4(recs: list[dict[str, Any]]) -> dict[tuple[int, int], np.ndarray]:
    """(winter_id, cd) -> (3,) probabilities from FDF rows."""
    out: dict[tuple[int, int], np.ndarray] = {}
    for rec in recs:
        if int(rec["month"]) != ISSUE_MONTH or int(rec["lead"]) != CPC_LEAD:
            continue
        winter_id = int(rec["year"]) + 1
        out[(winter_id, int(rec["cd"]))] = np.asarray(rec["p"], dtype=float)
    return out


def freeze_fdf_subset(
    *,
    temp_by_year: dict[int, tuple[str, str]],
    prcp_by_year: dict[int, tuple[str, str]],
    dest: Path,
) -> dict[str, Any]:
    """Freeze August lead-4 tercile probabilities from yearly FDF files. Not the live GIF."""
    tmap: dict[tuple[int, int], np.ndarray] = {}
    pmap: dict[tuple[int, int], np.ndarray] = {}
    shas: dict[str, str] = {}
    for year, (text, sha) in temp_by_year.items():
        tmap.update(_fdf_august_lead4(parse_fdf(text)))
        shas[f"temp_{year}"] = sha
    for year, (text, sha) in prcp_by_year.items():
        pmap.update(_fdf_august_lead4(parse_fdf(text)))
        shas[f"prcp_{year}"] = sha
    winters = sorted({wid for wid, _ in tmap} & {wid for wid, _ in pmap})
    rows = []
    for wid in winters:
        by_st = {}
        missing = False
        for sid, cd in STATION_CD.items():
            tp = tmap.get((wid, cd))
            pp = pmap.get((wid, cd))
            if tp is None or pp is None:
                missing = True
                break
            by_st[sid] = {"cd": cd, "tavg": [float(x) for x in tp], "prcp": [float(x) for x in pp]}
        if missing:
            continue
        rows.append({"winter_id": wid, "issue_year": wid - 1, "issue_month": ISSUE_MONTH, "lead": CPC_LEAD, "stations": by_st})
    if not rows:
        raise ArchiveError("no overlapping August lead-4 winters in FDF subset")
    payload = {
        "source": "cpcllftd.YYYY.dat / cpcllfpd.YYYY.dat",
        "live_lead4_forbidden": True,
        "shas": shas,
        "n_winters": len(rows),
        "rows": rows,
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def load_subset(path: Path) -> dict[tuple[str, int, str], np.ndarray]:
    _forbid_live_url(str(path))
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("live_lead4_forbidden") is not True:
        raise ArchiveError("subset must declare live_lead4_forbidden")
    out: dict[tuple[str, int, str], np.ndarray] = {}
    for row in payload["rows"]:
        wid = int(row["winter_id"])
        for sid, block in row["stations"].items():
            out[(sid, wid, "tavg")] = np.array(block["tavg"], dtype=float)
            out[(sid, wid, "prcp")] = np.array(block["prcp"], dtype=float)
    if not out:
        raise ArchiveError("empty CPC subset")
    return out
