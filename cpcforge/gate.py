# Copyright (c) 2026 Martial Systems LLC
"""Call sites for refuse laws."""

from __future__ import annotations

from typing import Any

from cpcforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from cpcforge.graphs.claim_bans import build_graph as build_claims
from cpcforge.graphs.completeness import build_graph as build_complete
from cpcforge.graphs.no_hero import build_graph as build_hero
from cpcforge.graphs.no_hydro import build_graph as build_hydro
from cpcforge.graphs.no_live_url import build_graph as build_url
from cpcforge.graphs.no_ridge import build_graph as build_ridge
from cpcforge.graphs.split_vars import build_graph as build_vars
from cpcforge.graphs.temporal_split import build_graph as build_split


def require_no_hydro(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_hydro"))
    state = {
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
    }
    state.update(flags)
    require_law(build_hydro(), state, allow_decisions=["allow"], law_id="cpc.no_hydro", thread_id=thread_id, raise_error=True)


def require_no_ridge(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_ridge"))
    state = {"ridge": False, "hgb": False, "sklearn_contestant": False}
    state.update(flags)
    require_law(build_ridge(), state, allow_decisions=["allow"], law_id="cpc.no_ridge", thread_id=thread_id, raise_error=True)


def require_no_live_url(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_url"))
    state = {"live_lead4": False}
    state.update(flags)
    require_law(build_url(), state, allow_decisions=["allow"], law_id="cpc.no_live_url", thread_id=thread_id, raise_error=True)


def require_completeness(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_complete"))
    state = {"floor_ok": False, "thin_kept": False}
    state.update(flags)
    require_law(build_complete(), state, allow_decisions=["allow"], law_id="cpc.completeness", thread_id=thread_id, raise_error=True)


def require_split(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_split"))
    state = {
        "temporal_ok": True,
        "confirm_in_train": False,
        "confirm_in_cuts": False,
        "random_split": False,
    }
    state.update(flags)
    require_law(build_split(), state, allow_decisions=["allow"], law_id="cpc.temporal_split", thread_id=thread_id, raise_error=True)


def require_split_vars(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_vars"))
    state = {"t_and_p_averaged": False, "tavg_present": True, "prcp_present": True}
    state.update(flags)
    require_law(build_vars(), state, allow_decisions=["allow"], law_id="cpc.split_vars", thread_id=thread_id, raise_error=True)


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_claims"))
    state = {
        "inches_forecast": False,
        "flood_warning": False,
        "p_sfha": False,
        "casualty": False,
        "frost_hero": False,
        "trust_the_stripe": False,
        "n_figures": 2,
    }
    state.update(flags)
    require_law(build_claims(), state, allow_decisions=["allow"], law_id="cpc.claim_bans", thread_id=thread_id, raise_error=True)


def require_no_hero(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "cpc_hero"))
    state = {
        "outlook_hero_rewritten": False,
        "cpc_win_as_hero": False,
        "readme_states_result": False,
    }
    state.update(flags)
    require_law(build_hero(), state, allow_decisions=["allow"], law_id="cpc.no_hero", thread_id=thread_id, raise_error=True)
