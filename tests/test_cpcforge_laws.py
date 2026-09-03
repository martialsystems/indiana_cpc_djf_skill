# Copyright (c) 2026 Martial Systems LLC

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from cpcforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError

from cpcforge.gate import (
    require_claims,
    require_completeness,
    require_no_hero,
    require_no_hydro,
    require_no_live_url,
    require_no_ridge,
    require_split,
    require_split_vars,
)
from cpcforge.product_laws import laws


def test_laws() -> None:
    require_no_hydro(thread_id="t.h.ok")
    with pytest.raises(LawBlockedError):
        require_no_hydro(p_sfha_feature=True, thread_id="t.h.p")
    require_no_ridge(thread_id="t.r.ok")
    with pytest.raises(LawBlockedError):
        require_no_ridge(ridge=True, thread_id="t.r.ridge")
    with pytest.raises(LawBlockedError):
        require_no_ridge(hgb=True, thread_id="t.r.hgb")
    require_no_live_url(thread_id="t.u.ok")
    with pytest.raises(LawBlockedError):
        require_no_live_url(live_lead4=True, thread_id="t.u.live")
    require_completeness(floor_ok=True, thread_id="t.c.ok")
    with pytest.raises(LawBlockedError):
        require_completeness(floor_ok=True, thin_kept=True, thread_id="t.c.thin")
    require_split(thread_id="t.s.ok")
    with pytest.raises(LawBlockedError):
        require_split(confirm_in_cuts=True, thread_id="t.s.cuts")
    require_split_vars(thread_id="t.v.ok")
    with pytest.raises(LawBlockedError):
        require_split_vars(t_and_p_averaged=True, thread_id="t.v.avg")
    require_claims(n_figures=2, thread_id="t.k.ok")
    with pytest.raises(LawBlockedError):
        require_claims(n_figures=3, thread_id="t.k.fig")
    require_no_hero(readme_states_result=True, thread_id="t.p.ok")
    with pytest.raises(LawBlockedError):
        require_no_hero(outlook_hero_rewritten=True, readme_states_result=True, thread_id="t.p.hero")
    assert {row["id"] for row in laws()} == {
        "cpc.no_hydro",
        "cpc.no_ridge",
        "cpc.no_live_url",
        "cpc.completeness",
        "cpc.temporal_split",
        "cpc.split_vars",
        "cpc.claim_bans",
        "cpc.no_hero",
    }
