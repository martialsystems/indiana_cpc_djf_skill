# Agent notes: indiana_cpc_djf_skill

Public GitHub. MIT. Question: Do issued CPC DJF temperature and precipitation outlooks beat climatology at South Bend, Fort Wayne, Indianapolis, and Evansville?

Live lock `b819355`: temperature Brier 0.643 vs equal chance 0.667 (yes); precipitation 0.809 vs 0.667 (no). Do not average it. Evansville precipitation 0.495 is a station row, not a statewide precip win. Contestant is issued CPC August lead 4. Last year is the second bar. Ridge and HGB stay off this tree. Confirmation DJF 2025-26 is out of train and out of tercile cuts. The live lead-4 URL is not the science lock. Result goes on the ledger either way. It does not rewrite the Winter outlook hero.

Do not edit `indiana_djf_snow_tercile`, `indiana_freeze_date`, `nwi_lake_effect_snow`, NWM trees, or Calumet maps. Do not restamp frozen science SHAs (`9aa7935`, `28941fb`, `ac36f0f`, `1416da1`, `6b47f21`). Do not regenerate the Stage B outlook GIFs. Do not read `p_sfha`, HAND, or White River 00060.

`cpcforge/` is the GraphForge pin.

Index: Temp lane on the live console. Precip gist gets one line.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`
