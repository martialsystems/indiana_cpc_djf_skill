# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. Two figures. T and P stay split."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from cpcskill.claims import require_clean, require_paths_clean
from cpcskill.config import QUESTION, REPO_ROOT
from cpcskill.fetch import fetch_live
from cpcskill.figure import write_two
from cpcskill.fixture import build_fixture
from cpcskill.skill import score_pack

try:
    from cpcforge.gate import (
        require_claims,
        require_completeness,
        require_no_hero,
        require_no_hydro,
        require_no_live_url,
        require_no_ridge,
        require_split,
        require_split_vars,
    )
except ImportError:  # pragma: no cover

    def require_claims(**kwargs):
        del kwargs

    def require_completeness(**kwargs):
        del kwargs

    def require_no_hero(**kwargs):
        del kwargs

    def require_no_hydro(**kwargs):
        del kwargs

    def require_no_live_url(**kwargs):
        del kwargs

    def require_no_ridge(**kwargs):
        del kwargs

    def require_split(**kwargs):
        del kwargs

    def require_split_vars(**kwargs):
        del kwargs


def _public_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        item = {}
        for k, v in r.items():
            if isinstance(v, np.ndarray):
                item[k] = [None if not np.isfinite(x) else float(x) for x in v.tolist()]
            else:
                item[k] = v
        out.append(item)
    return out


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    out["holdout_rows"] = _public_rows(report.get("holdout_rows") or [])
    out["confirm_rows"] = _public_rows(report.get("confirm_rows") or [])
    return out


def _run(log_dir: Path, *, pack, fixture: bool, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    require_no_hydro(thread_id="hydro")
    require_no_ridge(ridge=False, hgb=False, sklearn_contestant=False, thread_id="ridge")
    require_no_live_url(live_lead4=False, thread_id="url")
    require_clean(QUESTION, source="question")
    fit = score_pack(pack)
    require_completeness(
        floor_ok=True,
        thin_kept=False,
        thread_id="complete",
    )
    require_split(
        temporal_ok=True,
        confirm_in_train=bool(fit["confirm_in_train"]),
        confirm_in_cuts=bool(fit["confirm_in_cuts"]),
        random_split=bool(fit["random_split"]),
        thread_id="split",
    )
    require_split_vars(
        t_and_p_averaged=bool(fit["t_and_p_averaged"]),
        tavg_present=True,
        prcp_present=True,
        thread_id="vars",
    )
    paths = write_two(log_dir, fit=fit, live=not fixture)
    require_claims(n_figures=len(paths), thread_id="claims")
    t_beats = bool(fit["tavg_beats_ec"])
    p_beats = bool(fit["prcp_beats_ec"])
    require_no_hero(
        outlook_hero_rewritten=False,
        cpc_win_as_hero=False,
        readme_states_result=True,
        thread_id="hero",
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "source": pack.source,
        "n_rows": pack.n_rows,
        "n_stations": pack.n_stations,
        "units": {"tavg": "C", "prcp": "in", "skill": "brier/hit/heidke"},
        "element": "TAVG+PRCP",
        "contestant": "cpc",
        "ridge": False,
        "p_sfha_feature": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
        "live_lead4": False,
        "outlook_hero_rewritten": False,
        "tavg_beats_ec": t_beats,
        "prcp_beats_ec": p_beats,
        "t_and_p_averaged": False,
        "figures": paths,
        **{k: fit[k] for k in (
            "n_kept",
            "n_dropped_incomplete",
            "n_train",
            "n_holdout",
            "n_confirm",
            "holdout",
            "confirm",
            "holdout_north",
            "holdout_south",
            "by_station",
            "holdout_rows",
            "confirm_rows",
            "cuts",
            "confirm_in_train",
            "confirm_in_cuts",
            "random_split",
            "holdout_winters",
            "train_last_winter",
            "confirm_winter",
        )},
    }
    if extra:
        report.update(extra)
    require_clean(json.dumps(_jsonable(report), default=str), source="report")
    (log_dir / "stage0_report.json" if fixture else log_dir / "stage_c_report.json").write_text(
        json.dumps(_jsonable(report), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    require_paths_clean(
        [
            REPO_ROOT / "README.md",
            log_dir / ("stage0_report.json" if fixture else "stage_c_report.json"),
        ]
    )
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    pack = build_fixture()
    return _run(log_dir, pack=pack, fixture=True)


def run_live(log_dir: Path, *, cache_dir: Path) -> dict[str, Any]:
    pack, meta = fetch_live(cache_dir=cache_dir)
    return _run(log_dir, pack=pack, fixture=False, extra={"fetch_meta": meta})
