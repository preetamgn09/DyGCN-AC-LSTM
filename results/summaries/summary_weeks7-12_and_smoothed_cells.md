# Summary of 4 completed runs in /content/drive/MyDrive/dygcn_v3

## Abilene | target=raw | decoder=resid | start=12096

| model | own RMSE (mean ± sd) | raw-z RMSE | MASE | link WAPE | bottleneck | underprov@10% |
|---|---|---|---|---|---|---|
| Persistence | 0.8217 | 0.8217 | 1.765 | 0.200 | 0.303 | 0.252 |
| Seasonal-naive | 1.1228 | 1.1228 | 2.713 | 0.304 | 0.314 | 0.305 |
| Training-mean | 1.1690 | 1.1690 | 3.020 | 0.312 | 0.209 | 0.369 |
| Linear | 0.8201 ± 0.0161 | 0.8201 | 1.845 | 0.226 | 0.303 | 0.280 |
| AC-LSTM | 0.8174 ± 0.0011 | 0.8174 | 1.805 | 0.204 | 0.301 | 0.221 |
| DCRNN | 0.7537 ± 0.0010 | 0.7537 | 1.654 | 0.181 | 0.243 | 0.282 |
| DyGCN-AC-LSTM | 0.7485 ± 0.0030 | 0.7485 | 1.673 | 0.178 | 0.218 | 0.279 |
| DyGCN-static | 0.7498 ± 0.0027 | 0.7498 | 1.674 | 0.178 | 0.223 | 0.277 |

Paired seed tests (Holm):
- DyGCN-AC-LSTM − DCRNN: -0.0052 [-0.0084, -0.0019], p_Holm = 0.0227
- DyGCN-AC-LSTM − DyGCN-static: -0.0013 [-0.0025, -0.0001], p_Holm = 0.0401
- DyGCN-AC-LSTM − Linear: -0.0716 [-0.0946, -0.0485], p_Holm = 0.0030
- DyGCN-AC-LSTM − AC-LSTM: -0.0689 [-0.0728, -0.0649], p_Holm = 0.0000

Block-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:
- DyGCN-AC-LSTM|DCRNN: b1 [-0.0098, -0.0007]  b3 [-0.0097, -0.0011]  b5 [-0.0098, -0.0013]  b10 [-0.0102, -0.0018]
- DyGCN-AC-LSTM|DyGCN-static: b1 [-0.0030, +0.0002]  b3 [-0.0029, +0.0000]  b5 [-0.0030, +0.0000]  b10 [-0.0031, +0.0000]
- DyGCN-AC-LSTM|Linear: b1 [-0.1020, -0.0520]  b3 [-0.1039, -0.0524]  b5 [-0.1024, -0.0538]  b10 [-0.1022, -0.0544]
- DyGCN-AC-LSTM|AC-LSTM: b1 [-0.0785, -0.0590]  b3 [-0.0790, -0.0580]  b5 [-0.0792, -0.0591]  b10 [-0.0804, -0.0600]
- Linear|Persistence: b1 [-0.0238, +0.0316]  b3 [-0.0232, +0.0352]  b5 [-0.0231, +0.0336]  b10 [-0.0224, +0.0329]
- AC-LSTM|Persistence: b1 [-0.0066, -0.0017]  b3 [-0.0064, -0.0022]  b5 [-0.0065, -0.0023]  b10 [-0.0069, -0.0022]
- DCRNN|Persistence: b1 [-0.0773, -0.0590]  b3 [-0.0771, -0.0582]  b5 [-0.0772, -0.0588]  b10 [-0.0776, -0.0598]
- DyGCN-AC-LSTM|Persistence: b1 [-0.0836, -0.0625]  b3 [-0.0839, -0.0616]  b5 [-0.0845, -0.0626]  b10 [-0.0857, -0.0629]
- DyGCN-static|Persistence: b1 [-0.0822, -0.0613]  b3 [-0.0821, -0.0608]  b5 [-0.0822, -0.0621]  b10 [-0.0833, -0.0625]

## Abilene | target=smoothed | decoder=abs | start=0

| model | own RMSE (mean ± sd) | raw-z RMSE | MASE | link WAPE | bottleneck | underprov@10% |
|---|---|---|---|---|---|---|
| Persistence | 0.3361 | 0.6573 | 1.228 | 0.185 | 0.207 | 0.192 |
| Seasonal-naive | 1.3819 | 1.4071 | 2.369 | 0.438 | 0.592 | 0.306 |
| Training-mean | 1.1563 | 1.1846 | 3.396 | 0.558 | 0.435 | 0.771 |
| Persistence-raw-input | 0.3998 | 0.6981 | 1.272 | 0.212 | 0.354 | 0.176 |
| Linear | 0.6577 ± 0.0857 | 0.7853 | 1.862 | 0.359 | 0.299 | 0.566 |
| LSTM | 1.0166 ± 0.0037 | 1.0518 | 2.150 | 0.363 | 0.250 | 0.602 |
| AC-LSTM | 1.0114 ± 0.0031 | 1.0479 | 2.143 | 0.357 | 0.245 | 0.590 |
| DCRNN | 0.8019 ± 0.0032 | 0.8773 | 1.364 | 0.235 | 0.184 | 0.281 |
| STGCN | 0.7218 ± 0.0042 | 0.8177 | 1.347 | 0.225 | 0.190 | 0.298 |
| GWN | 0.7738 ± 0.0034 | 0.8552 | 1.280 | 0.199 | 0.213 | 0.250 |
| DyGCN-AC-LSTM | 0.8233 ± 0.0046 | 0.8954 | 1.384 | 0.234 | 0.177 | 0.271 |
| DyGCN-static | 0.8248 ± 0.0036 | 0.8963 | 1.384 | 0.232 | 0.177 | 0.270 |

Paired seed tests (Holm):
- DyGCN-AC-LSTM − DCRNN: +0.0214 [+0.0132, +0.0295], p_Holm = 0.0057
- DyGCN-AC-LSTM − STGCN: +0.1015 [+0.0954, +0.1076], p_Holm = 0.0000
- DyGCN-AC-LSTM − GWN: +0.0494 [+0.0450, +0.0539], p_Holm = 0.0000
- DyGCN-AC-LSTM − DyGCN-static: -0.0015 [-0.0034, +0.0003], p_Holm = 0.0772
- DyGCN-AC-LSTM − Linear: +0.1655 [+0.0620, +0.2690], p_Holm = 0.0227
- DyGCN-AC-LSTM − AC-LSTM: -0.1881 [-0.1934, -0.1829], p_Holm = 0.0000

Block-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:
- DyGCN-AC-LSTM|DCRNN: b1 [+0.0019, +0.0323]  b3 [+0.0018, +0.0328]  b5 [+0.0020, +0.0324]  b10 [+0.0025, +0.0324]
- DyGCN-AC-LSTM|STGCN: b1 [+0.0061, +0.1466]  b3 [+0.0066, +0.1464]  b5 [+0.0073, +0.1451]  b10 [+0.0074, +0.1451]
- DyGCN-AC-LSTM|GWN: b1 [+0.0134, +0.0656]  b3 [+0.0138, +0.0669]  b5 [+0.0144, +0.0657]  b10 [+0.0147, +0.0658]
- DyGCN-AC-LSTM|DyGCN-static: b1 [-0.0033, +0.0033]  b3 [-0.0032, +0.0029]  b5 [-0.0031, +0.0029]  b10 [-0.0031, +0.0029]
- DyGCN-AC-LSTM|Linear: b1 [-0.0993, +0.3022]  b3 [-0.0968, +0.2975]  b5 [-0.0946, +0.2954]  b10 [-0.0923, +0.2960]
- DyGCN-AC-LSTM|AC-LSTM: b1 [-0.1879, -0.1364]  b3 [-0.1910, -0.1374]  b5 [-0.1930, -0.1389]  b10 [-0.1959, -0.1419]
- Linear|Persistence: b1 [+0.0835, +0.1781]  b3 [+0.0894, +0.1819]  b5 [+0.0908, +0.1799]  b10 [+0.0932, +0.1779]
- LSTM|Persistence: b1 [+0.1504, +0.6714]  b3 [+0.1584, +0.6644]  b5 [+0.1608, +0.6603]  b10 [+0.1661, +0.6598]
- AC-LSTM|Persistence: b1 [+0.1512, +0.6628]  b3 [+0.1589, +0.6562]  b5 [+0.1613, +0.6526]  b10 [+0.1661, +0.6523]
- DCRNN|Persistence: b1 [+0.0076, +0.4480]  b3 [+0.0077, +0.4434]  b5 [+0.0083, +0.4395]  b10 [+0.0086, +0.4387]
- STGCN|Persistence: b1 [+0.0030, +0.3334]  b3 [+0.0029, +0.3293]  b5 [+0.0030, +0.3260]  b10 [+0.0037, +0.3256]
- GWN|Persistence: b1 [-0.0041, +0.4149]  b3 [-0.0044, +0.4110]  b5 [-0.0042, +0.4068]  b10 [-0.0038, +0.4067]
- DyGCN-AC-LSTM|Persistence: b1 [+0.0099, +0.4803]  b3 [+0.0104, +0.4750]  b5 [+0.0110, +0.4712]  b10 [+0.0114, +0.4707]
- DyGCN-static|Persistence: b1 [+0.0094, +0.4829]  b3 [+0.0096, +0.4782]  b5 [+0.0100, +0.4740]  b10 [+0.0109, +0.4738]

## Abilene | target=smoothed | decoder=resid | start=0

| model | own RMSE (mean ± sd) | raw-z RMSE | MASE | link WAPE | bottleneck | underprov@10% |
|---|---|---|---|---|---|---|
| Persistence | 0.3361 | 0.6573 | 1.228 | 0.185 | 0.207 | 0.192 |
| Seasonal-naive | 1.3819 | 1.4071 | 2.369 | 0.438 | 0.592 | 0.306 |
| Training-mean | 1.1563 | 1.1846 | 3.396 | 0.558 | 0.435 | 0.771 |
| Persistence-raw-input | 0.3998 | 0.6981 | 1.272 | 0.212 | 0.354 | 0.176 |
| Linear | 0.3786 ± 0.0271 | 0.6670 | 1.369 | 0.275 | 0.306 | 0.308 |
| LSTM | 0.3372 ± 0.0001 | 0.6583 | 1.235 | 0.188 | 0.213 | 0.186 |
| AC-LSTM | 0.3367 ± 0.0006 | 0.6577 | 1.230 | 0.190 | 0.216 | 0.187 |
| DCRNN | 0.3355 ± 0.0003 | 0.6562 | 1.229 | 0.187 | 0.207 | 0.193 |
| STGCN | 0.3314 ± 0.0029 | 0.6504 | 1.227 | 0.186 | 0.198 | 0.195 |
| GWN | 0.3257 ± 0.0004 | 0.6450 | 1.210 | 0.188 | 0.200 | 0.196 |
| DyGCN-AC-LSTM | 0.3338 ± 0.0013 | 0.6546 | 1.226 | 0.184 | 0.188 | 0.205 |
| DyGCN-static | 0.3322 ± 0.0005 | 0.6516 | 1.228 | 0.185 | 0.194 | 0.197 |

Paired seed tests (Holm):
- DyGCN-AC-LSTM − DCRNN: -0.0016 [-0.0032, -0.0001], p_Holm = 0.1136
- DyGCN-AC-LSTM − STGCN: +0.0024 [-0.0018, +0.0066], p_Holm = 0.1852
- DyGCN-AC-LSTM − GWN: +0.0081 [+0.0067, +0.0096], p_Holm = 0.0006
- DyGCN-AC-LSTM − DyGCN-static: +0.0016 [+0.0001, +0.0031], p_Holm = 0.1136
- DyGCN-AC-LSTM − Linear: -0.0447 [-0.0794, -0.0101], p_Holm = 0.0925
- DyGCN-AC-LSTM − AC-LSTM: -0.0028 [-0.0046, -0.0010], p_Holm = 0.0575

Block-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:
- DyGCN-AC-LSTM|DCRNN: b1 [-0.0028, -0.0010]  b3 [-0.0028, -0.0010]  b5 [-0.0026, -0.0010]  b10 [-0.0025, -0.0009]
- DyGCN-AC-LSTM|STGCN: b1 [-0.0012, +0.0101]  b3 [-0.0009, +0.0099]  b5 [-0.0009, +0.0097]  b10 [-0.0007, +0.0097]
- DyGCN-AC-LSTM|GWN: b1 [+0.0031, +0.0174]  b3 [+0.0032, +0.0171]  b5 [+0.0033, +0.0170]  b10 [+0.0034, +0.0169]
- DyGCN-AC-LSTM|DyGCN-static: b1 [-0.0017, +0.0078]  b3 [-0.0015, +0.0077]  b5 [-0.0014, +0.0075]  b10 [-0.0014, +0.0074]
- DyGCN-AC-LSTM|Linear: b1 [-0.0221, -0.0091]  b3 [-0.0192, -0.0101]  b5 [-0.0186, -0.0104]  b10 [-0.0177, -0.0108]
- DyGCN-AC-LSTM|AC-LSTM: b1 [-0.0047, -0.0012]  b3 [-0.0046, -0.0013]  b5 [-0.0045, -0.0014]  b10 [-0.0044, -0.0015]
- Linear|Persistence: b1 [+0.0058, +0.0197]  b3 [+0.0070, +0.0166]  b5 [+0.0072, +0.0164]  b10 [+0.0078, +0.0155]
- LSTM|Persistence: b1 [+0.0006, +0.0018]  b3 [+0.0006, +0.0018]  b5 [+0.0006, +0.0018]  b10 [+0.0006, +0.0018]
- AC-LSTM|Persistence: b1 [-0.0006, +0.0011]  b3 [-0.0006, +0.0011]  b5 [-0.0005, +0.0011]  b10 [-0.0005, +0.0011]
- DCRNN|Persistence: b1 [-0.0024, +0.0000]  b3 [-0.0023, +0.0000]  b5 [-0.0022, +0.0000]  b10 [-0.0022, +0.0000]
- STGCN|Persistence: b1 [-0.0137, -0.0009]  b3 [-0.0135, -0.0012]  b5 [-0.0131, -0.0012]  b10 [-0.0130, -0.0012]
- GWN|Persistence: b1 [-0.0210, -0.0049]  b3 [-0.0206, -0.0054]  b5 [-0.0203, -0.0054]  b10 [-0.0202, -0.0055]
- DyGCN-AC-LSTM|Persistence: b1 [-0.0037, -0.0015]  b3 [-0.0037, -0.0017]  b5 [-0.0035, -0.0017]  b10 [-0.0034, -0.0018]
- DyGCN-static|Persistence: b1 [-0.0113, -0.0004]  b3 [-0.0112, -0.0006]  b5 [-0.0108, -0.0006]  b10 [-0.0108, -0.0006]

## Geant | target=smoothed | decoder=abs | start=0

| model | own RMSE (mean ± sd) | raw-z RMSE | MASE | link WAPE | bottleneck | underprov@10% |
|---|---|---|---|---|---|---|
| Persistence | 0.4955 | 0.8032 | 1.378 | 0.146 | 0.088 | 0.364 |
| Seasonal-naive | 0.8719 | 1.0311 | 1.724 | 0.226 | 0.118 | 0.423 |
| Training-mean | 1.5287 | 1.6184 | 3.287 | 0.607 | 0.446 | 0.483 |
| Persistence-raw-input | 0.6555 | 0.9053 | 1.525 | 0.145 | 0.084 | 0.314 |
| Linear | 0.8960 ± 0.1472 | 1.0727 | 2.052 | 0.394 | 0.190 | 0.547 |
| LSTM | 1.2872 ± 0.0077 | 1.3959 | 2.770 | 0.534 | 0.397 | 0.465 |
| AC-LSTM | 1.2329 ± 0.0155 | 1.3482 | 2.702 | 0.516 | 0.379 | 0.487 |
| DCRNN | 0.6557 ± 0.0031 | 0.8940 | 1.603 | 0.275 | 0.106 | 0.525 |
| STGCN | 0.5998 ± 0.0118 | 0.8522 | 1.613 | 0.330 | 0.123 | 0.614 |
| GWN | 0.5791 ± 0.0045 | 0.8458 | 1.475 | 0.242 | 0.147 | 0.574 |
| DyGCN-AC-LSTM | 0.7229 ± 0.0023 | 0.9420 | 1.704 | 0.315 | 0.120 | 0.566 |
| DyGCN-static | 0.7129 ± 0.0036 | 0.9332 | 1.660 | 0.322 | 0.110 | 0.577 |

Paired seed tests (Holm):
- DyGCN-AC-LSTM − DCRNN: +0.0671 [+0.0636, +0.0707], p_Holm = 0.0000
- DyGCN-AC-LSTM − STGCN: +0.1231 [+0.1084, +0.1377], p_Holm = 0.0001
- DyGCN-AC-LSTM − GWN: +0.1438 [+0.1394, +0.1482], p_Holm = 0.0000
- DyGCN-AC-LSTM − DyGCN-static: +0.0100 [+0.0042, +0.0159], p_Holm = 0.0180
- DyGCN-AC-LSTM − Linear: -0.1731 [-0.3539, +0.0077], p_Holm = 0.0565
- DyGCN-AC-LSTM − AC-LSTM: -0.5100 [-0.5310, -0.4890], p_Holm = 0.0000

Block-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:
- DyGCN-AC-LSTM|DCRNN: b1 [+0.0444, +0.0514]  b3 [+0.0446, +0.0517]  b5 [+0.0440, +0.0517]  b10 [+0.0435, +0.0524]
- DyGCN-AC-LSTM|STGCN: b1 [+0.0807, +0.1015]  b3 [+0.0797, +0.1044]  b5 [+0.0791, +0.1036]  b10 [+0.0784, +0.1047]
- DyGCN-AC-LSTM|GWN: b1 [+0.0921, +0.1005]  b3 [+0.0916, +0.1010]  b5 [+0.0916, +0.1013]  b10 [+0.0917, +0.1020]
- DyGCN-AC-LSTM|DyGCN-static: b1 [+0.0050, +0.0124]  b3 [+0.0041, +0.0126]  b5 [+0.0042, +0.0130]  b10 [+0.0043, +0.0134]
- DyGCN-AC-LSTM|Linear: b1 [-0.1521, -0.1192]  b3 [-0.1506, -0.1205]  b5 [-0.1520, -0.1220]  b10 [-0.1535, -0.1216]
- DyGCN-AC-LSTM|AC-LSTM: b1 [-0.4254, -0.3858]  b3 [-0.4252, -0.3876]  b5 [-0.4278, -0.3887]  b10 [-0.4307, -0.3881]
- Linear|Persistence: b1 [+0.2462, +0.3099]  b3 [+0.2444, +0.3154]  b5 [+0.2439, +0.3173]  b10 [+0.2472, +0.3176]
- LSTM|Persistence: b1 [+0.5631, +0.6252]  b3 [+0.5613, +0.6326]  b5 [+0.5601, +0.6349]  b10 [+0.5669, +0.6336]
- AC-LSTM|Persistence: b1 [+0.5148, +0.5790]  b3 [+0.5137, +0.5874]  b5 [+0.5122, +0.5889]  b10 [+0.5190, +0.5866]
- DCRNN|Persistence: b1 [+0.0609, +0.1340]  b3 [+0.0613, +0.1392]  b5 [+0.0610, +0.1378]  b10 [+0.0644, +0.1362]
- STGCN|Persistence: b1 [+0.0249, +0.0833]  b3 [+0.0246, +0.0867]  b5 [+0.0241, +0.0861]  b10 [+0.0269, +0.0852]
- GWN|Persistence: b1 [+0.0153, +0.0850]  b3 [+0.0159, +0.0899]  b5 [+0.0156, +0.0880]  b10 [+0.0177, +0.0870]
- DyGCN-AC-LSTM|Persistence: b1 [+0.1088, +0.1832]  b3 [+0.1085, +0.1893]  b5 [+0.1083, +0.1877]  b10 [+0.1104, +0.1871]
- DyGCN-static|Persistence: b1 [+0.0987, +0.1771]  b3 [+0.0988, +0.1847]  b5 [+0.0983, +0.1825]  b10 [+0.1007, +0.1821]

## Factorial (first block): best learned model vs persistence, common scale

| data | target | decoder | best learned (raw-z RMSE) | persistence own-input | persistence raw-input | best link WAPE | persistence link WAPE |
|---|---|---|---|---|---|---|---|
| Abilene | smoothed | abs | Linear 0.7853 | 0.6573 | 0.6981 | 0.359 | 0.185 |
| Abilene | smoothed | resid | GWN 0.6450 | 0.6573 | 0.6981 | 0.188 | 0.185 |
| Geant | smoothed | abs | GWN 0.8458 | 0.8032 | 0.9053 | 0.242 | 0.146 |

## Rolling origins: DyGCN-AC-LSTM minus comparator (own-target RMSE; negative favors DyGCN)

## Compute (mean over seeds)

| run | model | params | train s/seed | ms/window | peak MB |
|---|---|---|---|---|---|
| Abilene_TM_raw_resid_start12096_v3 | Linear | 156 | 0 | 0.27 | 21 |
| Abilene_TM_raw_resid_start12096_v3 | AC-LSTM | 97,262 | 8 | 1.01 | 23 |
| Abilene_TM_raw_resid_start12096_v3 | DCRNN | 371,393 | 31 | 5.16 | 1776 |
| Abilene_TM_raw_resid_start12096_v3 | DyGCN-AC-LSTM | 150,081 | 82 | 15.84 | 1839 |
| Abilene_TM_raw_resid_start12096_v3 | DyGCN-static | 150,081 | 79 | 15.59 | 1799 |
| Abilene_TM_smoothed_abs_v3 | Linear | 156 | 0 | 0.26 | 21 |
| Abilene_TM_smoothed_abs_v3 | LSTM | 164,136 | 1 | 0.13 | 43 |
| Abilene_TM_smoothed_abs_v3 | AC-LSTM | 97,262 | 8 | 1.08 | 24 |
| Abilene_TM_smoothed_abs_v3 | DCRNN | 371,393 | 31 | 5.13 | 1776 |
| Abilene_TM_smoothed_abs_v3 | STGCN | 91,628 | 13 | 1.00 | 1788 |
| Abilene_TM_smoothed_abs_v3 | GWN | 138,980 | 9 | 0.94 | 525 |
| Abilene_TM_smoothed_abs_v3 | DyGCN-AC-LSTM | 150,081 | 83 | 15.73 | 1840 |
| Abilene_TM_smoothed_abs_v3 | DyGCN-static | 150,081 | 80 | 15.48 | 1799 |
| Abilene_TM_smoothed_resid_v3 | Linear | 156 | 0 | 0.27 | 21 |
| Abilene_TM_smoothed_resid_v3 | LSTM | 164,136 | 1 | 0.12 | 43 |
| Abilene_TM_smoothed_resid_v3 | AC-LSTM | 40,494 | 8 | 1.01 | 23 |
| Abilene_TM_smoothed_resid_v3 | DCRNN | 56,289 | 16 | 3.31 | 630 |
| Abilene_TM_smoothed_resid_v3 | STGCN | 91,628 | 13 | 0.82 | 1787 |
| Abilene_TM_smoothed_resid_v3 | GWN | 163,556 | 13 | 1.23 | 702 |
| Abilene_TM_smoothed_resid_v3 | DyGCN-AC-LSTM | 150,081 | 82 | 15.69 | 1839 |
| Abilene_TM_smoothed_resid_v3 | DyGCN-static | 150,081 | 79 | 15.41 | 1799 |
| Geant_TM_smoothed_abs_v3 | Linear | 156 | 0 | 0.75 | 30 |
| Geant_TM_smoothed_abs_v3 | LSTM | 574,392 | 1 | 0.14 | 61 |
| Geant_TM_smoothed_abs_v3 | AC-LSTM | 325,754 | 7 | 1.00 | 38 |
| Geant_TM_smoothed_abs_v3 | DCRNN | 223,169 | 104 | 9.06 | 5476 |
| Geant_TM_smoothed_abs_v3 | STGCN | 193,004 | 25 | 2.00 | 1252 |
| Geant_TM_smoothed_abs_v3 | GWN | 171,476 | 77 | 4.38 | 3138 |
| Geant_TM_smoothed_abs_v3 | DyGCN-AC-LSTM | 249,409 | 664 | 45.56 | 13111 |
| Geant_TM_smoothed_abs_v3 | DyGCN-static | 249,409 | 386 | 31.83 | 12365 |

## Tuning stability (selected by mean validation RMSE vs winner per tuning seed)

- Abilene_TM_raw_resid_start12096_v3 Linear: selected (0, 0); per-seed winners [(0, 0)]
- Abilene_TM_raw_resid_start12096_v3 AC-LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Abilene_TM_raw_resid_start12096_v3 DCRNN: selected (64, 3); per-seed winners [(64, 3)]
- Abilene_TM_raw_resid_start12096_v3 DyGCN-AC-LSTM: selected (64, 2); per-seed winners [(64, 2)]
- Abilene_TM_smoothed_abs_v3 Linear: selected (0, 0); per-seed winners [(0, 0)]
- Abilene_TM_smoothed_abs_v3 LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Abilene_TM_smoothed_abs_v3 AC-LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Abilene_TM_smoothed_abs_v3 DCRNN: selected (64, 3); per-seed winners [(64, 3)]
- Abilene_TM_smoothed_abs_v3 STGCN: selected (64, 3); per-seed winners [(64, 3)]
- Abilene_TM_smoothed_abs_v3 GWN: selected (32, 1); per-seed winners [(32, 1)]
- Abilene_TM_smoothed_abs_v3 DyGCN-AC-LSTM: selected (64, 2); per-seed winners [(64, 2)]
- Abilene_TM_smoothed_resid_v3 Linear: selected (0, 0); per-seed winners [(0, 0)]
- Abilene_TM_smoothed_resid_v3 LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Abilene_TM_smoothed_resid_v3 AC-LSTM: selected (32, 0); per-seed winners [(32, 0)]
- Abilene_TM_smoothed_resid_v3 DCRNN: selected (32, 2); per-seed winners [(32, 2)]
- Abilene_TM_smoothed_resid_v3 STGCN: selected (64, 3); per-seed winners [(64, 3)]
- Abilene_TM_smoothed_resid_v3 GWN: selected (32, 2); per-seed winners [(32, 2)]
- Abilene_TM_smoothed_resid_v3 DyGCN-AC-LSTM: selected (64, 2); per-seed winners [(64, 2)]
- Geant_TM_smoothed_abs_v3 Linear: selected (0, 0); per-seed winners [(0, 0)]
- Geant_TM_smoothed_abs_v3 LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Geant_TM_smoothed_abs_v3 AC-LSTM: selected (64, 0); per-seed winners [(64, 0)]
- Geant_TM_smoothed_abs_v3 DCRNN: selected (64, 2); per-seed winners [(64, 2)]
- Geant_TM_smoothed_abs_v3 STGCN: selected (64, 3); per-seed winners [(64, 3)]
- Geant_TM_smoothed_abs_v3 GWN: selected (32, 2); per-seed winners [(32, 2)]
- Geant_TM_smoothed_abs_v3 DyGCN-AC-LSTM: selected (64, 3); per-seed winners [(64, 3)]