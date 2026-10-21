# Reproducing every result in the paper

Each command below is one independent, resumable run that writes `<name>.json` to its output folder. If a run is interrupted, run the same command again: finished models are loaded instead of retrained, and a completed run exits immediately. Times are for one NVIDIA T4 GPU.

## First-period conditions (Tables I, II, IV, VI and Fig. 3)

**Abilene, smoothed target, absolute decoder (S-abs)** (about 30 min) → `Abilene_TM_smoothed_abs_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 12096 --target smoothed --outdir results/v3
```

**Abilene, smoothed target, residual decoder (S-res)** (about 30 min) → `Abilene_TM_smoothed_resid_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 12096 --target smoothed --residual --outdir results/v3
```

**Abilene, raw target, absolute decoder (R-abs)** (about 30 min) → `Abilene_TM_raw_abs_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 12096 --target raw --outdir results/v3
```

**Abilene, raw target, residual decoder (R-res; also weeks 1–6 of Table III)** (about 30 min) → `Abilene_TM_raw_resid_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 12096 --target raw --residual --outdir results/v3
```

**GÉANT, smoothed target, absolute decoder (S-abs)** (about 3.5 h) → `Geant_TM_smoothed_abs_v3.json`
```bash
python run_v3.py --path Geant_TM.csv --rm geant_rm.csv --sample-min 15 --min-active-frac 0 --target smoothed --outdir results/v3
```

**GÉANT, raw target, residual decoder (R-res)** (about 3.5 h) → `Geant_TM_raw_resid_v3.json`
```bash
python run_v3.py --path Geant_TM.csv --rm geant_rm.csv --sample-min 15 --min-active-frac 0 --target raw --residual --outdir results/v3
```

## Later Abilene periods (Table III and Fig. 2)

**Weeks 7–12** (about 25 min) → `Abilene_TM_raw_resid_start12096_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --start-step 12096 --max-steps 12096 --target raw --residual --models Linear AC-LSTM DCRNN DyGCN-AC-LSTM DyGCN-static --outdir results/v3
```

**Weeks 13–18** (about 25 min) → `Abilene_TM_raw_resid_start24192_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --start-step 24192 --max-steps 12096 --target raw --residual --models Linear AC-LSTM DCRNN DyGCN-AC-LSTM DyGCN-static --outdir results/v3
```

**Weeks 19–24** (about 25 min) → `Abilene_TM_raw_resid_start36288_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --start-step 36288 --max-steps 12096 --target raw --residual --models Linear AC-LSTM DCRNN DyGCN-AC-LSTM DyGCN-static --outdir results/v3
```

## Selection robustness (Section V-G)

**Three tuning seeds and a separately tuned fixed-graph model** (about 2.5 h) → `results/v3_tuning/Abilene_tunerobust_v3.json`
```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 12096 --target raw --residual --tune-seeds 0 1 2 --tune-static --models DCRNN DyGCN-AC-LSTM DyGCN-static --tag Abilene_tunerobust_v3 --outdir results/v3_tuning
```

## Compute (Table V)

Taken from the Abilene R-res and GÉANT S-abs runs above. Compute for GÉANT R-res was not measured: the archived run reloaded saved predictions and did not retrain.

## Building the tables

```bash
python summarize.py results/v3
python summarize.py results/v3_tuning
```

## Google Colab

Select a T4 GPU runtime, clone or upload this repository, and copy the four data files into it. Use a Google Drive folder as the output folder so results survive disconnections, and run one command per session at a time.
