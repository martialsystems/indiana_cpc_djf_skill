# Copyright (c) 2026 Martial Systems LLC

import numpy as np

from cpcskill.labels import assign_tercile, is_ec, issued_category, tercile_cuts


def test_tercile_and_ec() -> None:
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    lo, hi = tercile_cuts(y)
    cats = assign_tercile(y, lo, hi)
    assert set(cats.tolist()) == {0, 1, 2}
    p = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
    assert bool(is_ec(p)[0])
    assert int(issued_category(p)[0]) == 1
    lean = np.array([0.2, 0.2, 0.6])
    assert int(issued_category(lean)[0]) == 2
