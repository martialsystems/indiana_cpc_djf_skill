# Copyright (c) 2026 Martial Systems LLC
"""Live lead-4 GIF URL is not the science lock."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("live_lead4"):
        v.append("live_lead4")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="cpc.no_live_url", evaluate=_evaluate, extra=["live_lead4"])
