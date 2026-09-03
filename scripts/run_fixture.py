#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from cpcskill.pipeline import stage0_fixture  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "stage0_fixture"
    report = stage0_fixture(dest)
    print(report["question"])
    hold = report["holdout"]
    print("tavg CPC Brier", hold["tavg"]["cpc"]["brier"], "EC", hold["tavg"]["ec"]["brier"], "beats", report["tavg_beats_ec"])
    print("prcp CPC Brier", hold["prcp"]["cpc"]["brier"], "EC", hold["prcp"]["ec"]["brier"], "beats", report["prcp_beats_ec"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
