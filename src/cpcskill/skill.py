# Copyright (c) 2026 Martial Systems LLC
"""Hit rate, Heidke, Brier. CPC vs equal chance vs last year. T and P stay split."""

from __future__ import annotations

from typing import Any

import numpy as np

from cpcskill.config import (
    CAT_NEAR,
    CONFIRM_WINTER,
    CORE_IDS,
    CORE_STATIONS,
    EC_PROB,
    HOLDOUT_FIRST_WINTER,
    HOLDOUT_LAST_WINTER,
    NORTH_IDS,
    PRCP,
    SOUTH_IDS,
    TAVG,
    TRAIN_LAST_WINTER,
    VARIABLES,
)
from cpcskill.labels import assign_tercile, is_ec, issued_category, tercile_cuts
from cpcskill.pack import SeasonPack
from cpcskill.split import CONFIRM, HOLDOUT, TRAIN, role

_EC_BRIER = float(np.sum((np.array([EC_PROB, EC_PROB, EC_PROB]) - np.array([1.0, 0.0, 0.0])) ** 2))


def _one_hot(cat: int) -> np.ndarray:
    o = np.zeros(3, dtype=float)
    o[int(cat)] = 1.0
    return o


def _brier_row(p: np.ndarray, cat: int) -> float:
    return float(np.sum((np.asarray(p, dtype=float) - _one_hot(cat)) ** 2))


def _heidke_vs_third(hit: float) -> float:
    return float((hit - EC_PROB) / (1.0 - EC_PROB))


def _score_rows(rows: list[dict[str, Any]], variable: str) -> dict[str, Any]:
    if not rows:
        return {
            "n": 0,
            "cpc": {"brier": None, "hit": None, "heidke": None, "n_non_ec": 0, "hit_non_ec": None, "heidke_non_ec": None, "coverage_non_ec": 0.0},
            "ec": {"brier": _EC_BRIER, "hit": EC_PROB},
            "last_year": {"brier": None, "hit": None, "n": 0},
            "beats_ec": False,
        }
    p_key = "p_tavg" if variable == TAVG else "p_prcp"
    rows = [r for r in rows if np.all(np.isfinite(r[p_key]))]
    if not rows:
        return {
            "n": 0,
            "cpc": {"brier": None, "hit": None, "heidke": None, "n_non_ec": 0, "hit_non_ec": None, "heidke_non_ec": None, "coverage_non_ec": 0.0},
            "ec": {"brier": _EC_BRIER, "hit": EC_PROB},
            "last_year": {"brier": None, "hit": None, "n": 0},
            "beats_ec": False,
        }
    obs = np.array([r[f"obs_{variable}"] for r in rows], dtype=int)
    probs = np.vstack([r[p_key] for r in rows])
    issued = issued_category(probs)
    ec_mask = is_ec(probs)
    cpc_brier = float(np.mean([_brier_row(probs[i], int(obs[i])) for i in range(len(rows))]))
    cpc_hit = float(np.mean(issued == obs))
    non = ~ec_mask
    n_non = int(np.sum(non))
    if n_non:
        hit_non = float(np.mean(issued[non] == obs[non]))
        heidke_non = _heidke_vs_third(hit_non)
    else:
        hit_non = None
        heidke_non = None
    ly_rows = [r for r in rows if r.get(f"ly_{variable}") is not None]
    if ly_rows:
        ly_hit = float(np.mean([int(r[f"ly_{variable}"]) == int(r[f"obs_{variable}"]) for r in ly_rows]))
        ly_brier = float(np.mean([_brier_row(_one_hot(int(r[f"ly_{variable}"])), int(r[f"obs_{variable}"])) for r in ly_rows]))
    else:
        ly_hit = None
        ly_brier = None
    beats = cpc_brier < _EC_BRIER - 1e-12
    return {
        "n": len(rows),
        "cpc": {
            "brier": cpc_brier,
            "hit": cpc_hit,
            "heidke": _heidke_vs_third(cpc_hit),
            "n_non_ec": n_non,
            "hit_non_ec": hit_non,
            "heidke_non_ec": heidke_non,
            "coverage_non_ec": float(n_non) / float(len(rows)),
        },
        "ec": {"brier": _EC_BRIER, "hit": EC_PROB},
        "last_year": {"brier": ly_brier, "hit": ly_hit, "n": len(ly_rows)},
        "beats_ec": beats,
    }


def _attach_categories(pack: SeasonPack) -> tuple[list[dict[str, Any]], dict[str, dict[str, tuple[float, float]]], bool, bool]:
    rows: list[dict[str, Any]] = []
    for i in range(pack.n_rows):
        rows.append(
            {
                "station_id": str(pack.station_id[i]),
                "name": str(pack.name[i]),
                "winter_id": int(pack.winter_id[i]),
                "role": role(int(pack.winter_id[i])),
                "tavg_c": float(pack.tavg_c[i]),
                "prcp_in": float(pack.prcp_in[i]),
                "tavg_frac": float(pack.tavg_frac[i]),
                "prcp_frac": float(pack.prcp_frac[i]),
                "p_tavg": np.asarray(pack.p_tavg[i], dtype=float),
                "p_prcp": np.asarray(pack.p_prcp[i], dtype=float),
            }
        )
    cuts: dict[str, dict[str, tuple[float, float]]] = {TAVG: {}, PRCP: {}}
    for sid, _ in CORE_STATIONS:
        train_t = np.array([r["tavg_c"] for r in rows if r["station_id"] == sid and r["role"] == TRAIN], dtype=float)
        train_p = np.array([r["prcp_in"] for r in rows if r["station_id"] == sid and r["role"] == TRAIN], dtype=float)
        cuts[TAVG][sid] = tercile_cuts(train_t)
        cuts[PRCP][sid] = tercile_cuts(train_p)
    by_key = {(r["station_id"], r["winter_id"]): r for r in rows}
    for r in rows:
        sid = r["station_id"]
        r["obs_tavg"] = int(assign_tercile(np.array([r["tavg_c"]]), *cuts[TAVG][sid])[0])
        r["obs_prcp"] = int(assign_tercile(np.array([r["prcp_in"]]), *cuts[PRCP][sid])[0])
        prev = by_key.get((sid, r["winter_id"] - 1))
        r["ly_tavg"] = None if prev is None else int(prev["obs_tavg"])
        r["ly_prcp"] = None if prev is None else int(prev["obs_prcp"])
    confirm_ids = {r["winter_id"] for r in rows if r["role"] == CONFIRM}
    train_ids = {r["winter_id"] for r in rows if r["role"] == TRAIN}
    return rows, cuts, bool(confirm_ids & train_ids), CONFIRM_WINTER in train_ids


def score_pack(pack: SeasonPack) -> dict[str, Any]:
    rows, cuts, confirm_in_train, confirm_in_cuts = _attach_categories(pack)
    hold = [r for r in rows if r["role"] == HOLDOUT]
    confirm = [r for r in rows if r["role"] == CONFIRM]
    north = [r for r in hold if r["station_id"] in NORTH_IDS]
    south = [r for r in hold if r["station_id"] in SOUTH_IDS]

    def by_var(subset: list[dict[str, Any]]) -> dict[str, Any]:
        return {TAVG: _score_rows(subset, TAVG), PRCP: _score_rows(subset, PRCP)}

    by_station: dict[str, Any] = {}
    for sid, name in CORE_STATIONS:
        sub = [r for r in hold if r["station_id"] == sid]
        by_station[sid] = {"name": name, **by_var(sub)}

    t_beats = bool(by_var(hold)[TAVG]["beats_ec"])
    p_beats = bool(by_var(hold)[PRCP]["beats_ec"])
    holdout_vars = by_var(hold)
    return {
        "n_kept": len(rows),
        "n_train": sum(1 for r in rows if r["role"] == TRAIN),
        "n_holdout": len(hold),
        "n_confirm": len(confirm),
        "n_dropped_incomplete": int((pack.extra or {}).get("n_dropped_incomplete") or 0),
        "holdout": holdout_vars,
        "confirm": by_var(confirm),
        "holdout_north": by_var(north),
        "holdout_south": by_var(south),
        "by_station": by_station,
        "tavg_beats_ec": t_beats,
        "prcp_beats_ec": p_beats,
        "t_and_p_averaged": False,
        "contestant": "cpc",
        "confirm_in_train": confirm_in_train,
        "confirm_in_cuts": confirm_in_cuts,
        "random_split": False,
        "train_last_winter": TRAIN_LAST_WINTER,
        "holdout_winters": list(range(HOLDOUT_FIRST_WINTER, HOLDOUT_LAST_WINTER + 1)),
        "confirm_winter": CONFIRM_WINTER,
        "cuts": {
            sid: {
                TAVG: {"lo": cuts[TAVG][sid][0], "hi": cuts[TAVG][sid][1]},
                PRCP: {"lo": cuts[PRCP][sid][0], "hi": cuts[PRCP][sid][1]},
            }
            for sid, _ in CORE_STATIONS
        },
        "holdout_rows": hold,
        "confirm_rows": confirm,
        "core_ids": list(CORE_IDS),
        "ec_near_default": CAT_NEAR,
    }
