# Copyright (c) 2026 Martial Systems LLC
"""Contestant is CPC. Ridge and HGB stay off this tree."""

from __future__ import annotations

from typing import Any

from cpcforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in ("ridge", "hgb", "sklearn_contestant") if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="cpc.no_ridge", evaluate=_evaluate, extra=["ridge", "hgb", "sklearn_contestant"])
