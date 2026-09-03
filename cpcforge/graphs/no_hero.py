# Copyright (c) 2026 Martial Systems LLC
"""A CPC win does not rewrite the Winter outlook hero."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("outlook_hero_rewritten"):
        v.append("outlook_hero_rewritten")
    if state.get("cpc_win_as_hero"):
        v.append("cpc_win_as_hero")
    if not state.get("readme_states_result"):
        v.append("readme_silent")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="cpc.no_hero",
        evaluate=_evaluate,
        extra=["outlook_hero_rewritten", "cpc_win_as_hero", "readme_states_result"],
    )
