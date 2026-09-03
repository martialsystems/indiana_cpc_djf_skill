# Copyright (c) 2026 Martial Systems LLC
"""Locked CPC DJF skill vs equal-chance climatology at four Indiana cores."""

from __future__ import annotations

from pathlib import Path

QUESTION = (
    "Do issued CPC DJF temperature and precipitation outlooks beat climatology "
    "at South Bend, Fort Wayne, Indianapolis, and Evansville?"
)
USER_AGENT = "MartialSystemsResearch/indiana_cpc_djf_skill"
MAX_FIGURES = 2
COMPLETE_FRAC = 0.80
MIN_TRAIN_WINTERS = 20
EC_PROB = 1.0 / 3.0
EC_TOL = 0.005
ISSUE_MONTH = 8
CPC_LEAD = 4
N_FORECAST_DIVISIONS = 102
MM_PER_INCH = 25.4

# winter_id is the January year. DJF 2018-19 is 2019.
TRAIN_FIRST_WINTER = 1992  # DJF 1991-92
TRAIN_LAST_WINTER = 2019
HOLDOUT_FIRST_WINTER = 2020
HOLDOUT_LAST_WINTER = 2025
CONFIRM_WINTER = 2026
CLIMATE_FIRST = 1991
CLIMATE_LAST = 2020

CORE_STATIONS = (
    ("USW00014848", "South Bend"),
    ("USW00014827", "Fort Wayne"),
    ("USW00093819", "Indianapolis"),
    ("USW00093817", "Evansville"),
)
CORE_IDS = tuple(s for s, _ in CORE_STATIONS)
NORTH_IDS = ("USW00014848", "USW00014827")
SOUTH_IDS = ("USW00093819", "USW00093817")

# Nearest of CPC's 102 forecast divisions by centroid. Frozen before skill.
# 23 Southern Michigan, 24 East-central Illinois, 39 Western Kentucky.
STATION_CD = {
    "USW00014848": 23,
    "USW00014827": 23,
    "USW00093819": 24,
    "USW00093817": 39,
}

TAVG = "tavg"
PRCP = "prcp"
VARIABLES = (TAVG, PRCP)
CAT_BELOW = 0
CAT_NEAR = 1
CAT_ABOVE = 2
CAT_NAMES = ("below", "near", "above")

GHCND_STATION_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{sid}.csv.gz"
GHCND_STATIONS_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
CPC_TEMP_URL = "https://www.cpc.ncep.noaa.gov/pacdir/NFORdir/HUGEdir2/cpcllft.dat"
CPC_PRCP_URL = "https://www.cpc.ncep.noaa.gov/pacdir/NFORdir/HUGEdir2/cpcllfp.dat"
CPC_FDF_TEMP = "https://www.cpc.ncep.noaa.gov/pacdir/NFORdir/HUGEdir2/cpcllftd.{year}.dat"
CPC_FDF_PRCP = "https://www.cpc.ncep.noaa.gov/pacdir/NFORdir/HUGEdir2/cpcllfpd.{year}.dat"
CPC_REGDICT_URL = "https://www.cpc.ncep.noaa.gov/pacdir/NFORdir/HUGEdir2/regdict.txt"
FDF_ISSUE_YEARS = tuple(range(2019, 2026))  # holdout + confirmation issue years
LIVE_LEAD4_TEMP = "https://www.cpc.ncep.noaa.gov/products/predictions/long_range/lead04/off04_temp.gif"
LIVE_LEAD4_PRCP = "https://www.cpc.ncep.noaa.gov/products/predictions/long_range/lead04/off04_prcp.gif"

INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
TEMP_GIST = "https://gist.github.com/martialsystems/e5de316dbb5f672573906572730e3735"
PRECIP_GIST = "https://gist.github.com/martialsystems/b5f900aad37487bb8c0206a321c1ed5c"
CONSOLE_URL = "https://martialsystems.github.io/indiana_wx_pages/"
SNOW_SHA = "9aa7935"
FREEZE_SHA = "28941fb"
AMOUNT_SHA = "ac36f0f"
JJA_MISS_SHA = "1416da1"
WINTER_LAKE_SHA = "6b47f21"

REPO_ROOT = Path(__file__).resolve().parents[2]

LIVE_BARS_SUBTITLE = (
    "Holdout Brier. CPC vs equal chance vs last year. Skill, not a winter forecast."
)
LIVE_NORTH_SUBTITLE = (
    "Holdout temperature Brier. North vs south. Split, not a statewide stripe."
)
FIXTURE_BARS_SUBTITLE = "Fixture planted CPC skill. Does not rescue live."
FIXTURE_NORTH_SUBTITLE = "Fixture north vs south temperature. Does not rescue live."
