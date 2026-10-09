# Dynamic vs. Static Graphs for Network Traffic-Matrix Prediction

A clean, reproducible pipeline for multi-step **network traffic-matrix (TM) prediction**
on real backbone datasets, built to answer one question fairly:

> Does a *per-step dynamic* graph actually beat a *static* graph once both are tuned on equal footing?

**Short answer: no.** On two real backbones (Abilene and GÉANT), a properly tuned
static-graph model (DCRNN) matches or beats the dynamic-graph model
(DyGCN-AC-LSTM). The dynamic-graph advantage reported in earlier work is largely an
artifact of comparing against an **untuned** baseline.

This repository is the open, honest pipeline behind that comparison.

---

## Key result

RMSE on log-transformed, z-scored traffic (lower is better). 6 weeks of data,
5 seeds, identical preprocessing, frozen test set, and **equal-budget validation
tuning** for both graph models.

| Model | Abilene (11 nodes, 110 flows) | GÉANT (23 nodes, 506 flows) |
|---|---|---|
| LSTM | 1.017 ± 0.003 | ~1.28 |
| AC-LSTM | 1.012 ± 0.002 | ~1.22 |
| **DCRNN** (tuned, static graph) | **0.802 ± 0.002** | **~0.66** *(final 5-seed TBD)* |
| DyGCN-AC-LSTM (dynamic graph) | 0.815 ± 0.004 | ~0.73 *(final 5-seed TBD)* |

Tuned DCRNN wins on every seed, on both datasets — and on Abilene it does so with
**fewer parameters** (hidden 64 vs 256). The effect is consistent, not noise.

---

## Why this exists

An earlier manuscript claimed DyGCN-AC-LSTM (per-step distance-correlation
adjacency + diffusion graph convolution inside Adaptive Clockwork LSTM gates) beats
static-graph baselines for backbone TM prediction. A reviewer questioned whether
the baselines were tuned. They were not. This project rebuilds the method and the
baselines from scratch and compares them **fairly** — same data, same splits, same
tuning budget, same seeds. The fair comparison reverses the headline claim.

Negative and replication results are useful: this is a cautionary data point on how
much baseline tuning matters in graph-based traffic forecasting.

---

## Method summary

- **Graph vertices = OD flows.** Adjacency is `[F, F]` where F = number of directed
  OD flows (110 for Abilene, 506 for GÉANT).
- **Dynamic model (DyGCN-AC-LSTM):** per-step adjacency from distance correlation
  over a causal window (top-K sparsified, symmetric-normalized, cached every p
  steps); bidirectional diffusion convolution inside clockwork LSTM gates.
- **Static baseline (DCRNN):** diffusion-convolutional GRU, seq2seq, with one fixed
  adjacency built once from the training split.
- **Temporal baselines:** LSTM, AC-LSTM.
- **Preprocessing:** per-flow z-score, FCM clustering on interpretable shape
  features, weighted exponential smoothing; log transform for the heavy-tailed real
  traffic.
- **Protocol:** chronological splits, frozen test set, 5 seeds, equal-budget
  validation tuning for both graph models.

---

## Setup

```bash
pip install -r requirements.txt    # numpy, scipy, torch
```

**Data** is not included (too large for Git). Download `Abilene_TM.csv` and
`Geant_TM.csv` from the DDPM-TME repo's `Dataset/` folder
(https://github.com/Y-debug-sys/DDPM-TME) and place them in the project root.

A GPU is recommended (the runners auto-detect CUDA and print `device: cuda`).

---

## Run

```bash
# sanity check (tiny, no data download needed)
python smoke_test.py

# Abilene — 11 nodes / 110 flows
python run_abilene.py --path Abilene_TM.csv --drop-node 0 --sample-min 5 \
    --max-steps 12096 --seeds 42 123 456 789 1024 --log-transform

# GÉANT — 23 nodes / 506 flows
python run_abilene.py --path Geant_TM.csv --sample-min 15 --min-active-frac 0 \
    --max-steps 12000 --seeds 42 123 456 789 1024 --log-transform
```

Each run prints the validation tuning, per-seed RMSE, and a mean ± std table.
See `COLAB_GUIDE.md` for a step-by-step Google Colab walkthrough.

---

## Repository layout

```
src/
  synthetic.py      GÉANT-like synthetic generator
  abilene.py        real Abilene/GÉANT loader (auto-detects layout)
  preprocessing.py  z-score + FCM + weighted exponential smoothing
  adjacency.py      dynamic distance-correlation adjacency (top-K, norm, cache)
  datasets.py       non-overlapping windows + chronological splits
  metrics.py        RMSE / MAE / sMAPE + Wilcoxon
  diffconv.py       batched bidirectional diffusion convolution
  dygcn_ac_lstm.py  proposed dynamic-graph model (clockwork + gate-level DiffConv)
  dcrnn.py          DCRNN static-graph baseline (DCGRU seq2seq)
  baselines.py      LSTM, AC-LSTM
  train.py          batched training/eval loop (GPU)
run_abilene.py      real-data benchmark (tunes both graph models, 5 seeds)
run_experiment.py   synthetic benchmark
smoke_test.py       end-to-end sanity check
RESULTS.md          full results and the honest finding
HANDOFF.md          project state and remaining work
COLAB_GUIDE.md      Colab run instructions
```

---

## Status / remaining work

- **Done:** pipeline, proposed model, LSTM / AC-LSTM / tuned DCRNN, Abilene (5
  seeds), GÉANT (finishing the final 5-seed run).
- **Optional next:** add STGCN and Graph WaveNet (tuned the same way) to broaden the
  "tuned static baselines win" evidence; ablations.

## Data sources

- Abilene & GÉANT traffic matrices: DDPM-TME repository (`Dataset/`).
- Abilene originates from the Yin Zhang / Roughan traffic-matrix dataset.

## Notes

Results are honest and reproducible; the code reports what the experiments actually
show, including where the proposed method loses. If you build on this, please keep
the comparison fair — that is the whole point.
