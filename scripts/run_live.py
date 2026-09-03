#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND TAVG/PRCP vs issued CPC August DJF. Empty core stops."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from cpcskill.errors import FetchError  # noqa: E402
from cpcskill.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw"
    try:
        report = run_live(dest, cache_dir=cache)
    except FetchError as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    hold = report["holdout"]
    print("tavg CPC Brier", round(hold["tavg"]["cpc"]["brier"], 4), "EC", round(hold["tavg"]["ec"]["brier"], 4), "beats", report["tavg_beats_ec"])
    print("prcp CPC Brier", round(hold["prcp"]["cpc"]["brier"], 4), "EC", round(hold["prcp"]["ec"]["brier"], 4), "beats", report["prcp_beats_ec"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
