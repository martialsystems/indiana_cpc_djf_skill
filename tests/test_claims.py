# Copyright (c) 2026 Martial Systems LLC

import pytest

from cpcskill.claims import require_clean, scan_text
from cpcskill.errors import ClaimBanError


def test_allowed_and_banned() -> None:
    assert scan_text("issued CPC DJF outlooks vs equal chance. Brier against climatology.") == []
    assert "inches_forecast" in scan_text("Indiana will get 20 inches")
    assert "flood_warning" in scan_text("flood warning tonight")
    assert "p_sfha" in scan_text("p_sfha as a winter score")
    assert "trust_the_stripe" in scan_text("trust the stripe this winter")
    assert "hgb_contestant" in scan_text("HGB Brier 0.22 vs CPC")
    assert "em_dash" in scan_text("skill — not a forecast")
    with pytest.raises(ClaimBanError):
        require_clean("will get 12 inches", source="t")
