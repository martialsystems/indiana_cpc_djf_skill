# Methodology: issued CPC DJF vs equal-chance climatology

Question: Do issued CPC DJF temperature and precipitation outlooks beat climatology at South Bend, Fort Wayne, Indianapolis, and Evansville?

## Label

GHCND daily `TAVG` (°C) and `PRCP` (inches). DJF is 1 Dec through 28/29 Feb.

Temperature: seasonal mean of daily TAVG. If TAVG is missing, `(TMAX+TMIN)/2` only when both exist that day.

Precipitation: seasonal sum of daily PRCP.

Drop a station-winter under 80% of DJF days. Empty TAVG or PRCP for a required core stops. SNOW cannot substitute for PRCP. TMIN-only cannot substitute for TAVG.

Observed terciles: 33rd and 67th percentiles of that station's train DJF TAVG and DJF PRCP. Holdout and confirmation do not set cuts.

## Stations

Required cores: South Bend `USW00014848`, Fort Wayne `USW00014827`, Indianapolis `USW00093819`, Evansville `USW00093817`.

North: South Bend and Fort Wayne. South: Indianapolis and Evansville.

Valparaiso and Michigan City stay out.

## Contestant

August-issued CPC DJF outlook, CPC lead 4. Same lead as the 20 Aug 2026 maps on the research console.

Numeric lock: yearly CPC forecast-distribution files `cpcllftd.YYYY.dat` / `cpcllfpd.YYYY.dat` (the running `cpcllft.dat` on the same server stops in 1999). August lead-4 rows, Gaussian tercile probabilities from forecast vs climatology mean and sd, sampled at the frozen forecast divisions:

| Station | Forecast division |
|---------|-------------------|
| South Bend | 23 Southern Michigan |
| Fort Wayne | 23 Southern Michigan |
| Indianapolis | 24 East-central Illinois |
| Evansville | 39 Western Kentucky |

The live lead-4 GIF URL is not the science lock. Ridge and HGB stay off this tree.

## Bars

Bar A: equal-chance climatology. Brier of `(1/3, 1/3, 1/3)`. Hit rate vs 1/3. Heidke vs random.

Bar B: last year's observed tercile at that station. Reported. Not the question.

## Split

Train: DJF 1991-92 through 2018-19 (winter_id 1992 through 2019). Tercile cuts only.

Holdout: DJF 2019-20 through 2024-25 (winter_id 2020 through 2025).

Confirmation: DJF 2025-26 (winter_id 2026), out of train and out of cuts. Cannot reverse the holdout.

DJF 2026-27 is the field being contextualized, not a score row.

## Metrics

Lead with holdout Brier vs equal chance. Heidke and hit rate second. Per-station table required. North vs south table required for temperature. Temperature and precipitation are not averaged into one yes/no. A 7/24 count is not the method.

Issued category: argmax of `(below, near, above)`. Equal chance when all three are 0.333.

When CPC issued equal chances, non-EC Heidke is skipped if coverage is 0, and Brier equals climatology by construction.

## Figures

1. Holdout Brier bars: CPC vs equal chance vs last year, temperature and precipitation panels.
2. North vs south temperature Brier. Split, not a statewide stripe.

Two figures max.

## Fixture

Synthetic DJF TAVG/PRCP at the four cores with planted CPC skill. Fixture skill does not rescue live.
