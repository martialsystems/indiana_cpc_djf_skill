# Copyright (c) 2026 Martial Systems LLC
"""Station-winter DJF TAVG and PRCP plus issued CPC probabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SeasonPack:
    station_id: np.ndarray
    name: np.ndarray
    winter_id: np.ndarray
    tavg_c: np.ndarray
    prcp_in: np.ndarray
    tavg_frac: np.ndarray
    prcp_frac: np.ndarray
    p_tavg: np.ndarray
    p_prcp: np.ndarray
    source: str = "fixture"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def n_rows(self) -> int:
        return int(self.station_id.shape[0])

    @property
    def n_stations(self) -> int:
        return int(np.unique(self.station_id).shape[0])
