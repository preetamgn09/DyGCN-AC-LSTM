# Summary of 1 completed runs in /content/drive/MyDrive/dygcn_v3_tuning

## Abilene | target=raw | decoder=resid | start=0

| model | own RMSE (mean ± sd) | raw-z RMSE | MASE | link WAPE | bottleneck | underprov@10% |
|---|---|---|---|---|---|---|
| Persistence | 0.6981 | 0.6981 | 1.272 | 0.212 | 0.354 | 0.176 |
| Seasonal-naive | 1.4268 | 1.4268 | 2.450 | 0.472 | 0.704 | 0.295 |
| Training-mean | 1.1846 | 1.1846 | 3.396 | 0.558 | 0.435 | 0.771 |
| DCRNN | 0.6631 ± 0.0003 | 0.6631 | 1.228 | 0.199 | 0.223 | 0.310 |
| DyGCN-AC-LSTM | 0.6740 ± 0.0021 | 0.6740 | 1.249 | 0.194 | 0.206 | 0.277 |
| DyGCN-static-tuned | 0.6745 ± 0.0021 | 0.6745 | 1.255 | 0.195 | 0.206 | 0.282 |
| DyGCN-static | 0.6745 ± 0.0021 | 0.6745 | 1.255 | 0.195 | 0.206 | 0.282 |

Paired seed tests (Holm):
- DyGCN-AC-LSTM − DCRNN: +0.0110 [+0.0085, +0.0135], p_Holm = 0.0008
- DyGCN-AC-LSTM − DyGCN-static: -0.0004 [-0.0014, +0.0005], p_Holm = 0.5574
- DyGCN-AC-LSTM − DyGCN-static-tuned: -0.0004 [-0.0014, +0.0005], p_Holm = 0.5574

Block-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:
- DyGCN-AC-LSTM|DCRNN: b1 [+0.0053, +0.0171]  b3 [+0.0054, +0.0171]  b5 [+0.0055, +0.0171]  b10 [+0.0053, +0.0171]
- DyGCN-AC-LSTM|DyGCN-static: b1 [-0.0015, +0.0003]  b3 [-0.0016, +0.0003]  b5 [-0.0016, +0.0003]  b10 [-0.0016, +0.0003]
- DyGCN-AC-LSTM|DyGCN-static-tuned: b1 [-0.0015, +0.0003]  b3 [-0.0016, +0.0003]  b5 [-0.0016, +0.0003]  b10 [-0.0016, +0.0003]
- DCRNN|Persistence: b1 [-0.0475, -0.0287]  b3 [-0.0491, -0.0279]  b5 [-0.0487, -0.0266]  b10 [-0.0499, -0.0249]
- DyGCN-AC-LSTM|Persistence: b1 [-0.0392, -0.0170]  b3 [-0.0410, -0.0159]  b5 [-0.0401, -0.0151]  b10 [-0.0413, -0.0133]
- DyGCN-static-tuned|Persistence: b1 [-0.0381, -0.0168]  b3 [-0.0396, -0.0160]  b5 [-0.0390, -0.0150]  b10 [-0.0402, -0.0132]
- DyGCN-static|Persistence: b1 [-0.0381, -0.0168]  b3 [-0.0396, -0.0160]  b5 [-0.0390, -0.0150]  b10 [-0.0402, -0.0132]

## Factorial (first block): best learned model vs persistence, common scale

| data | target | decoder | best learned (raw-z RMSE) | persistence own-input | persistence raw-input | best link WAPE | persistence link WAPE |
|---|---|---|---|---|---|---|---|
| Abilene | raw | resid | DCRNN 0.6631 | 0.6981 | 0.6981 | 0.199 | 0.212 |

## Rolling origins: DyGCN-AC-LSTM minus comparator (own-target RMSE; negative favors DyGCN)

## Compute (mean over seeds)

| run | model | params | train s/seed | ms/window | peak MB |
|---|---|---|---|---|---|
| Abilene_tunerobust_v3 | DCRNN | 371,393 | 31 | 5.05 | 1774 |
| Abilene_tunerobust_v3 | DyGCN-AC-LSTM | 150,081 | 82 | 15.75 | 1839 |
| Abilene_tunerobust_v3 | DyGCN-static-tuned | 150,081 | 80 | 15.34 | 1799 |
| Abilene_tunerobust_v3 | DyGCN-static | 150,081 | 80 | 15.43 | 1799 |

## Tuning stability (selected by mean validation RMSE vs winner per tuning seed)

- Abilene_tunerobust_v3 DCRNN: selected (64, 3); per-seed winners [(64, 3), (64, 2), (64, 3)]
- Abilene_tunerobust_v3 DyGCN-AC-LSTM: selected (64, 2); per-seed winners [(64, 2), (64, 2), (64, 2)]
- Abilene_tunerobust_v3 DyGCN-static-tuned: selected (64, 2); per-seed winners [(64, 2), (64, 2), (64, 2)]