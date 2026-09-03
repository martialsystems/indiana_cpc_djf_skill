# Copyright (c) 2026 Martial Systems LLC
"""This tree does not read p_sfha, HAND, Nora Q, or NWM."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in ("p_sfha_feature", "p_sfha_label", "hand_feature", "nora_q", "nwm_file") if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="cpc.no_hydro",
        evaluate=_evaluate,
        extra=["p_sfha_feature", "p_sfha_label", "hand_feature", "nora_q", "nwm_file"],
    )
