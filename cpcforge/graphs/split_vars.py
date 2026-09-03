# Copyright (c) 2026 Martial Systems LLC
"""Temperature and precipitation are not averaged into one yes/no."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("t_and_p_averaged"):
        v.append("t_and_p_averaged")
    if not state.get("tavg_present"):
        v.append("tavg_missing")
    if not state.get("prcp_present"):
        v.append("prcp_missing")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="cpc.split_vars",
        evaluate=_evaluate,
        extra=["t_and_p_averaged", "tavg_present", "prcp_present"],
    )
