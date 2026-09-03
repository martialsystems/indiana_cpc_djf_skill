# Copyright (c) 2026 Martial Systems LLC
"""80% DJF completeness. Thin cores are not kept."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("floor_ok"):
        v.append("floor")
    if state.get("thin_kept"):
        v.append("thin_kept")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="cpc.completeness", evaluate=_evaluate, extra=["floor_ok", "thin_kept"])
