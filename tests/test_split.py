# Copyright (c) 2026 Martial Systems LLC

import pytest

from cpcskill.errors import SplitError
from cpcskill.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def test_pinned_winters() -> None:
    assert role(2019) == TRAIN
    assert role(2020) == HOLDOUT
    assert role(2025) == HOLDOUT
    assert role(2026) == CONFIRM
    assert role(1992) == TRAIN
    assert role(1991) != TRAIN


def test_confirm_leak_refused() -> None:
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=True, confirm_in_cuts=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_cuts=True, random_split=False)
