# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

import pytest

from cpcskill.errors import FetchError
from cpcskill.fetch import fetch_live


def test_empty_core_stops(tmp_path: Path) -> None:
    def getter(url: str) -> bytes:
        if "ghcnd-stations" in url:
            return b"USW00014848  41.7000  -86.3100  237.1 SOUTH BEND          IN US\n"
        if "USW00014848" in url:
            return b""
        raise AssertionError(url)

    with pytest.raises(FetchError, match="empty GHCND"):
        fetch_live(cache_dir=tmp_path, getter=getter)
