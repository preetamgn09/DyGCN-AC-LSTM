# Results — fair comparison on real backbone data

All RMSE values are on log-transformed, z-scored traffic (lower = better),
6 weeks of data, 5 seeds (except where noted), graph vertices = OD flows.
All graph models use identical preprocessing, identical chronological splits
with a FROZEN test set, and equal-budget validation tuning (4 configs each).

## Headline finding
When the static-graph baseline (DCRNN) is tuned fairly, it MATCHES OR BEATS the
proposed dynamic-graph model (DyGCN-AC-LSTM) on both real datasets. The dynamic-
graph advantage reported in the original manuscript does not survive a fair
comparison — it was an artifact of comparing against an untuned baseline.

## Abilene (11 nodes, 110 flows) — 5 seeds, COMPLETE
| Model                | RMSE (mean ± std) |
|----------------------|-------------------|
| LSTM                 | 1.017 ± 0.003     |
| AC-LSTM              | 1.012 ± 0.002     |
| DCRNN (tuned, static)| **0.802 ± 0.002** |
| DyGCN-AC-LSTM        | 0.815 ± 0.004     |

Tuned DCRNN beats the proposed model on all 5 seeds. Gap (~0.013) is several
times the seed noise. Note: DCRNN wins with hidden=64 vs the proposed model's
256 — fewer parameters, better result.

## GEANT (23 nodes, 506 flows) — consistent with Abilene
Same pattern, wider margin — tuned DCRNN beats the proposed model on all 5 seeds.

| Model                | RMSE (mean ± std) |
|----------------------|-------------------|
| LSTM                 | 1.287 ± 0.007     |
| AC-LSTM              | 1.233 ± 0.012     |
| DCRNN (tuned, static)| **0.660 ± 0.010** |
| DyGCN-AC-LSTM        | 0.728 ± 0.011     |

## What this means
- The "dynamic graph beats static graph" claim for backbone TM prediction does
  not hold once the static baseline is tuned on the same budget.
- This is a clean, reproducible, two-dataset result — the basis for an honest
  cautionary / replication paper, NOT a "our method wins" paper.

## Reproduce
```bash
python run_abilene.py --path Abilene_TM.csv --drop-node 0 --sample-min 5 \
    --max-steps 12096 --seeds 42 123 456 789 1024 --log-transform
python run_abilene.py --path Geant_TM.csv --sample-min 15 --min-active-frac 0 \
    --max-steps 12000 --seeds 42 123 456 789 1024 --log-transform
```
