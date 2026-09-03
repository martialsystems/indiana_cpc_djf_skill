# Copyright (c) 2026 Martial Systems LLC


class GateError(RuntimeError):
    """Stage hard gate failed."""


class ClaimBanError(GateError):
    """Report text hit a banned claim."""


class FetchError(GateError):
    """GHCND TAVG/PRCP empty for a required core, or a refused substitute."""


class SplitError(GateError):
    """Temporal split leaked confirmation into train or tercile cuts."""


class FigureCapError(GateError):
    """This tree stops at two figures."""


class ArchiveError(GateError):
    """CPC issued probabilities missing or a live lead-4 URL was used as the lock."""
