# Copyright (c) 2026 Martial Systems LLC
"""Temporal split. Confirmation is out of train and out of tercile cuts."""

from __future__ import annotations

from cpcskill.config import CONFIRM_WINTER, HOLDOUT_FIRST_WINTER, HOLDOUT_LAST_WINTER, TRAIN_FIRST_WINTER, TRAIN_LAST_WINTER
from cpcskill.errors import SplitError

TRAIN = "train"
HOLDOUT = "holdout"
CONFIRM = "confirm"
OTHER = "other"


def role(winter_id: int) -> str:
    y = int(winter_id)
    if TRAIN_FIRST_WINTER <= y <= TRAIN_LAST_WINTER:
        return TRAIN
    if HOLDOUT_FIRST_WINTER <= y <= HOLDOUT_LAST_WINTER:
        return HOLDOUT
    if y == CONFIRM_WINTER:
        return CONFIRM
    return OTHER


def assert_split(*, confirm_in_train: bool, confirm_in_cuts: bool, random_split: bool) -> None:
    if confirm_in_train or confirm_in_cuts:
        raise SplitError("confirmation leaked into train or tercile cuts")
    if random_split:
        raise SplitError("random row split is refused")
