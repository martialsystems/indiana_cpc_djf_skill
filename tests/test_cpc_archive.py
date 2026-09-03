# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

import numpy as np
import pytest

from cpcskill.cpc_archive import extract_august_lead4, parse_cpcllf, station_probs
from cpcskill.errors import ArchiveError


def _record(year: int, month: int, lead: int, below: float, near: float, above: float) -> str:
    hdr = f"{year} {month} {lead} 102 950"
    b = " ".join([str(below)] * 102)
    n = " ".join([str(near)] * 102)
    a = " ".join([str(above)] * 102)
    return f"{hdr} {b} {n} {a}"


def test_parse_and_august_lead4() -> None:
    text = " ".join(
        [
            _record(2019, 8, 4, 0.20, 0.30, 0.50),
            _record(2019, 11, 1, 0.10, 0.20, 0.70),
            _record(2020, 8, 4, 0.40, 0.30, 0.30),
        ]
    )
    recs = parse_cpcllf(text)
    assert len(recs) == 3
    mapped = extract_august_lead4(recs)
    assert set(mapped) == {2020, 2021}
    p = station_probs(mapped[2020], "USW00014848")
    assert p.tolist() == pytest.approx([0.20, 0.30, 0.50])


def test_live_url_refused(tmp_path: Path) -> None:
    from cpcskill.cpc_archive import load_or_fetch

    with pytest.raises(ArchiveError):
        load_or_fetch("https://www.cpc.ncep.noaa.gov/products/predictions/long_range/lead04/off04_temp.gif", tmp_path / "x")


def test_gaussian_ec_and_fdf_freeze(tmp_path: Path) -> None:
    from cpcskill.cpc_archive import freeze_fdf_subset, gaussian_tercile_probs, parse_fdf

    p = gaussian_tercile_probs(26.0, 3.0, 26.0, 3.0)
    assert p.tolist() == pytest.approx([1 / 3, 1 / 3, 1 / 3], abs=1e-6)
    warm = gaussian_tercile_probs(28.0, 3.0, 26.0, 3.0)
    assert warm[2] > warm[0]
    line23 = "2019   8   4  23 0.32 20.92 22.12 23.17 24.45 25.38 26.16 26.89 27.65 28.43 29.37 30.65 31.70 32.89 26.89 26.77 2.9115 3.0700"
    line24 = line23.replace("  23 ", "  24 ")
    line39 = line23.replace("  23 ", "  39 ")
    blob = "\n".join([line23, line24, line39])
    recs = parse_fdf(line23)
    assert recs[0]["cd"] == 23
    assert recs[0]["lead"] == 4
    dest = tmp_path / "august_lead4.json"
    payload = freeze_fdf_subset(
        temp_by_year={2019: (blob, "t")},
        prcp_by_year={2019: (blob.replace("26.89 26.77 2.9115 3.0700", "6.56 6.41 0.7833 0.8000 0.7200"), "p")},
        dest=dest,
    )
    assert payload["live_lead4_forbidden"] is True
    assert payload["n_winters"] == 1
    assert payload["rows"][0]["stations"]["USW00014848"]["cd"] == 23
