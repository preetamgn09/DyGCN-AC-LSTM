# Result files

`v3/` and `v3_tuning/` hold the JSON files written by `run_v3.py` for every run reported in the paper (predictions are not included because of their size; they can be regenerated with the commands in `REPRODUCE.md`).

Expected files:

- `v3/Abilene_TM_smoothed_abs_v3.json`
- `v3/Abilene_TM_smoothed_resid_v3.json`
- `v3/Abilene_TM_raw_abs_v3.json`
- `v3/Abilene_TM_raw_resid_v3.json`
- `v3/Abilene_TM_raw_resid_start12096_v3.json`
- `v3/Abilene_TM_raw_resid_start24192_v3.json`
- `v3/Abilene_TM_raw_resid_start36288_v3.json`
- `v3/Geant_TM_smoothed_abs_v3.json`
- `v3/Geant_TM_raw_resid_v3.json`
- `v3_tuning/Abilene_tunerobust_v3.json`

`summaries/` contains the summaries printed by `summarize.py` for these runs.
