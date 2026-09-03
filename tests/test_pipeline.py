# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from cpcskill.config import QUESTION
from cpcskill.errors import FigureCapError
from cpcskill.figure import _cap
from cpcskill.pipeline import stage0_fixture


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["figures"] == ["skill_bars.png", "north_south.png"]
    assert (tmp_path / "skill_bars.png").is_file()
    assert (tmp_path / "north_south.png").is_file()
    assert report["contestant"] == "cpc"
    assert report["ridge"] is False
    assert report["live_lead4"] is False
    assert report["t_and_p_averaged"] is False
    assert report["p_sfha_feature"] is False
    assert report["nwm_file"] is False
    assert report["confirm_in_train"] is False
    assert report["confirm_in_cuts"] is False
    assert report["holdout_winters"] == [2020, 2021, 2022, 2023, 2024, 2025]
    assert report["confirm_winter"] == 2026
    assert report["tavg_beats_ec"] is True
    assert "USW00014848" in report["by_station"]
    assert "USW00093817" in report["by_station"]
    t = report["holdout"]["tavg"]
    p = report["holdout"]["prcp"]
    assert t["cpc"]["brier"] < t["ec"]["brier"]
    assert p["n"] == t["n"]
    assert t["n"] == 24


def test_live_holdout_split() -> None:
    import json

    path = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    live = json.loads(path.read_text(encoding="utf-8"))
    assert live["contestant"] == "cpc"
    assert live["t_and_p_averaged"] is False
    assert live["live_lead4"] is False
    assert live["tavg_beats_ec"] is True
    assert live["prcp_beats_ec"] is False
    assert live["n_holdout"] == 24
    assert live["n_train"] == 112
    assert live["confirm_in_cuts"] is False
    t = live["holdout"]["tavg"]
    p = live["holdout"]["prcp"]
    assert t["cpc"]["brier"] < t["ec"]["brier"]
    assert p["cpc"]["brier"] > p["ec"]["brier"]
    assert live["holdout_north"]["tavg"]["beats_ec"] is True
    assert live["holdout_south"]["tavg"]["beats_ec"] is True
    ev = live["by_station"]["USW00093817"]["prcp"]
    assert ev["cpc"]["brier"] < ev["ec"]["brier"]


def test_third_figure_refused() -> None:
    try:
        _cap(3)
        raise AssertionError("cap allowed 3")
    except FigureCapError:
        pass
