# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from cpcforge.graphs.claim_bans import build_graph as claim_bans
    from cpcforge.graphs.completeness import build_graph as completeness
    from cpcforge.graphs.no_hero import build_graph as no_hero
    from cpcforge.graphs.no_hydro import build_graph as no_hydro
    from cpcforge.graphs.no_live_url import build_graph as no_live_url
    from cpcforge.graphs.no_ridge import build_graph as no_ridge
    from cpcforge.graphs.split_vars import build_graph as split_vars
    from cpcforge.graphs.temporal_split import build_graph as temporal_split

    return [
        {
            "id": "cpc.no_hydro",
            "build": no_hydro,
            "state": {
                "p_sfha_feature": False,
                "p_sfha_label": False,
                "hand_feature": False,
                "nora_q": False,
                "nwm_file": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.no_ridge",
            "build": no_ridge,
            "state": {"ridge": False, "hgb": False, "sklearn_contestant": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.no_live_url",
            "build": no_live_url,
            "state": {"live_lead4": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.completeness",
            "build": completeness,
            "state": {"floor_ok": True, "thin_kept": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.temporal_split",
            "build": temporal_split,
            "state": {
                "temporal_ok": True,
                "confirm_in_train": False,
                "confirm_in_cuts": False,
                "random_split": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.split_vars",
            "build": split_vars,
            "state": {"t_and_p_averaged": False, "tavg_present": True, "prcp_present": True},
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.claim_bans",
            "build": claim_bans,
            "state": {
                "inches_forecast": False,
                "flood_warning": False,
                "p_sfha": False,
                "casualty": False,
                "frost_hero": False,
                "trust_the_stripe": False,
                "n_figures": 2,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "cpc.no_hero",
            "build": no_hero,
            "state": {
                "outlook_hero_rewritten": False,
                "cpc_win_as_hero": False,
                "readme_states_result": True,
            },
            "allow_decisions": ["allow"],
        },
    ]
