# Copyright (c) 2026 Martial Systems LLC
"""Synthetic four cores with planted CPC skill. Does not rescue live."""

from __future__ import annotations

import numpy as np

from cpcskill.config import (
    COMPLETE_FRAC,
    CONFIRM_WINTER,
    CORE_STATIONS,
    EC_PROB,
    HOLDOUT_FIRST_WINTER,
    HOLDOUT_LAST_WINTER,
    TRAIN_LAST_WINTER,
)
from cpcskill.pack import SeasonPack


def build_fixture() -> SeasonPack:
    rng = np.random.default_rng(7)
    winters = list(range(1992, CONFIRM_WINTER + 1))
    station_id: list[str] = []
    name: list[str] = []
    winter_id: list[int] = []
    tavg: list[float] = []
    prcp: list[float] = []
    p_t: list[list[float]] = []
    p_p: list[list[float]] = []
    for i, (sid, nm) in enumerate(CORE_STATIONS):
        base_t = -2.0 + 2.5 * i
        base_p = 6.0 + 1.5 * i
        for wid in winters:
            wave = np.sin((wid - 1992) / 3.0 + i)
            t = base_t + 3.0 * wave + 0.15 * rng.normal()
            p = max(1.0, base_p + 4.0 * wave + 0.2 * rng.normal())
            station_id.append(sid)
            name.append(nm)
            winter_id.append(wid)
            tavg.append(t)
            prcp.append(p)
            hold = HOLDOUT_FIRST_WINTER <= wid <= HOLDOUT_LAST_WINTER
            if hold:
                # Plant a lean on the eventual above/below using the wave sign.
                if wave >= 0:
                    pt = [0.15, 0.20, 0.65]
                    pp = [0.20, 0.25, 0.55]
                else:
                    pt = [0.65, 0.20, 0.15]
                    pp = [0.55, 0.25, 0.20]
                if i == 3 and wid % 2 == 0:
                    pp = [EC_PROB, EC_PROB, EC_PROB]
            else:
                pt = [EC_PROB, EC_PROB, EC_PROB]
                pp = [EC_PROB, EC_PROB, EC_PROB]
            p_t.append(pt)
            p_p.append(pp)
    n = len(station_id)
    return SeasonPack(
        station_id=np.array(station_id, dtype=object),
        name=np.array(name, dtype=object),
        winter_id=np.array(winter_id, dtype=int),
        tavg_c=np.array(tavg, dtype=float),
        prcp_in=np.array(prcp, dtype=float),
        tavg_frac=np.full(n, 0.95),
        prcp_frac=np.full(n, 0.95),
        p_tavg=np.array(p_t, dtype=float),
        p_prcp=np.array(p_p, dtype=float),
        source="fixture",
        extra={
            "n_dropped_incomplete": 1,
            "planted": True,
            "complete_frac": COMPLETE_FRAC,
            "train_last_winter": TRAIN_LAST_WINTER,
        },
    )
