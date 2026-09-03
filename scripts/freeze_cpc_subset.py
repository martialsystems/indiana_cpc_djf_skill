#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Download CPC ASCII archives and freeze August lead-4 rows for the four cores."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from cpcskill.config import CPC_FDF_PRCP, CPC_FDF_TEMP, FDF_ISSUE_YEARS  # noqa: E402
from cpcskill.cpc_archive import freeze_fdf_subset, load_or_fetch, sha256_bytes  # noqa: E402


def main() -> int:
    cache = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data" / "raw" / "cpc"
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else cache / "august_lead4.json"
    temp_by_year = {}
    prcp_by_year = {}
    for year in FDF_ISSUE_YEARS:
        tbody = load_or_fetch(CPC_FDF_TEMP.format(year=year), cache / f"cpcllftd.{year}.dat")
        pbody = load_or_fetch(CPC_FDF_PRCP.format(year=year), cache / f"cpcllfpd.{year}.dat")
        temp_by_year[year] = (tbody.decode("utf-8", errors="replace"), sha256_bytes(tbody))
        prcp_by_year[year] = (pbody.decode("utf-8", errors="replace"), sha256_bytes(pbody))
    payload = freeze_fdf_subset(temp_by_year=temp_by_year, prcp_by_year=prcp_by_year, dest=dest)
    print("n_winters", payload["n_winters"])
    print("winters", [r["winter_id"] for r in payload["rows"]])
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
