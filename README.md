# DyGCN-AC-LSTM: matched re-evaluation code

Code and results for the paper *"Revisiting Dynamic Graph Convolution for Network Traffic-Matrix Prediction: A Matched Evaluation Against Tuned Static and Naive Baselines."*

The repository contains the dynamic-graph model (DyGCN-AC-LSTM), its same-cell fixed-graph ablation, the baselines (DCRNN, STGCN, Graph WaveNet, LSTM, AC-LSTM, a linear forecaster, and naive forecasts), and the scripts that produce every result in the paper.

## Contents

| Path | Purpose |
|---|---|
| `run_v3.py` | Runs one experimental condition end to end: preprocessing, validation search, five evaluation seeds, statistics, common-scale and link-level metrics. Resumable. |
| `summarize.py` | Rebuilds every results table from the JSON result files. |
| `compare_results.py` | Compares a re-run with an archived result file. |
| `src/` | Models, preprocessing, dynamic adjacency, training, metrics, statistics. STGCN, Graph WaveNet, and the linear forecaster are in `src/extra_models.py`; link-level metrics are in `src/operational.py`. |
| `results/v3/`, `results/v3_tuning/` | The JSON result files behind the paper. |
| `results/summaries/` | Human-readable summaries of those runs, as produced by `summarize.py`. |
| `logs/` | Console output of runs executed on Google Colab (NVIDIA T4), including the smoke test. |
| `smoke_test.py` | Older CPU-only smoke test on synthetic data (core models only). |
| `run_abilene.py`, `run_experiment.py`, `run_revision.py` | Legacy scripts from earlier rounds of the study; not used for the paper. |

## Requirements

Python 3.10 or later, `numpy`, `scipy`, and PyTorch 2.x (`pip install -r requirements.txt`). A GPU is strongly recommended; the paper's runs used one NVIDIA T4 on Google Colab.

## Data

The traffic matrices and routing matrices are not redistributed. Download them from the DDPM-TME repository:

```bash
git clone --depth 1 https://github.com/Y-debug-sys/DDPM-TME.git
```

and copy `Abilene_TM.csv`, `Geant_TM.csv`, `abilene_rm.csv`, and `geant_rm.csv` into the repository root.

## Quick check (about 10 minutes on a T4 GPU)

```bash
python run_v3.py --path Abilene_TM.csv --rm abilene_rm.csv --drop-node 0 --sample-min 5 --max-steps 6048 --target raw --residual --epochs 1 --seeds 42 --fixed LSTM=32 AC-LSTM=32 DCRNN=32,2 STGCN=32,2 GWN=16,1 DyGCN-AC-LSTM=32,2 --outdir smoke
```

It passes if it prints a final table that includes every model, link-level metrics, and a compute table. The expected output is in `logs/smoke_test_run_v3_colab.txt`.

## Reproducing the paper

`REPRODUCE.md` lists the command for every condition and the table or figure it feeds. To rebuild the tables from the archived results without retraining:

```bash
python summarize.py results/v3
python summarize.py results/v3_tuning
```

To check a re-run against the archive:

```bash
python compare_results.py results/v3/<file>.json <your_outdir>/<file>.json
```

GPU training is not bit-for-bit deterministic; differences of up to about 0.002 RMSE are expected.
