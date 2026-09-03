# Copyright (c) 2026 Martial Systems LLC
"""Train-only tercile cuts. Completeness on DJF days."""

from __future__ import annotations

import calendar
from datetime import date

import numpy as np

from cpcskill.config import CAT_ABOVE, CAT_BELOW, CAT_NEAR, COMPLETE_FRAC, EC_PROB, EC_TOL


def djf_ndays(winter_id: int) -> int:
    feb = 29 if calendar.isleap(int(winter_id)) else 28
    return 31 + feb + 31


def complete_enough(n_present: int, winter_id: int, *, floor: float = COMPLETE_FRAC) -> bool:
    return (n_present / float(djf_ndays(winter_id))) >= floor


def winter_id_of(day: date) -> int:
    return day.year + 1 if day.month == 12 else day.year


def tercile_cuts(train: np.ndarray) -> tuple[float, float]:
    y = np.asarray(train, dtype=float)
    y = y[np.isfinite(y)]
    if y.size < 6:
        raise ValueError("not enough train winters for terciles")
    lo, hi = np.percentile(y, [100.0 / 3.0, 200.0 / 3.0])
    return float(lo), float(hi)


def assign_tercile(values: np.ndarray, lo: float, hi: float) -> np.ndarray:
    y = np.asarray(values, dtype=float)
    out = np.full(y.shape, CAT_NEAR, dtype=np.int32)
    out[y < lo] = CAT_BELOW
    out[y > hi] = CAT_ABOVE
    return out


def is_ec(p: np.ndarray, *, tol: float = EC_TOL) -> np.ndarray:
    arr = np.asarray(p, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return np.all(np.abs(arr - EC_PROB) <= tol, axis=1)


def issued_category(p: np.ndarray) -> np.ndarray:
    arr = np.asarray(p, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    cat = np.argmax(arr, axis=1).astype(np.int32)
    cat[is_ec(arr)] = CAT_NEAR
    return cat
