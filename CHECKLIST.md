# Operator checklist

1. Fixture Stage 0 green. Fixture does not rescue live.
2. Freeze CPC August lead-4 subset from `cpcllft.dat` / `cpcllfp.dat`. Do not scrape the live lead-4 GIF into the lock.
3. GHCND TAVG and PRCP fetch-or-stop on the four cores. SNOW cannot substitute for PRCP. TMIN-only cannot substitute for TAVG.
4. Train through DJF 2018-19. Holdout DJF 2019-20 through 2024-25. Confirmation DJF 2025-26 out of the cuts.
5. Lead with Brier vs equal chance. Locked `b819355`: temperature 0.643 vs 0.667; precipitation 0.809 vs 0.667. Temperature and precipitation stay split. Per-station table. North vs south for temperature. Evansville precipitation 0.495 is not a statewide precip win.
6. Two figures. Result on the ledger either way. Outlook hero stays CPC plus normals.
7. Do not edit DJF snow, freeze-date, NWM, Calumet, or restamp frozen science SHAs.
8. Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3 (Temp lane)
