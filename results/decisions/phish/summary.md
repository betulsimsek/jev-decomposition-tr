# Results

## accuracy

| arm | EN |
|---|---|
| B-raw | 0.778 [0.758, 0.796] |
| B-fit | 0.778 [0.759, 0.796] |
| M-raw | 0.889 [0.875, 0.902] |
| M-fit | 0.889 [0.875, 0.902] |
| D-noisyor | 0.755 [0.737, 0.773] |
| D-fit | 0.964 [0.955, 0.971] |
| MD-fit | 0.974 [0.967, 0.981] |

## macro_f1

| arm | EN |
|---|---|
| B-raw | 0.773 [0.756, 0.793] |
| B-fit | 0.777 [0.759, 0.796] |
| M-raw | 0.889 [0.876, 0.902] |
| M-fit | 0.889 [0.875, 0.903] |
| D-noisyor | 0.740 [0.721, 0.760] |
| D-fit | 0.963 [0.954, 0.971] |
| MD-fit | 0.974 [0.967, 0.981] |

## auc

| arm | EN |
|---|---|
| B-raw | 0.858 [0.841, 0.873] |
| B-fit | 0.858 [0.842, 0.874] |
| M-raw | 0.960 [0.952, 0.967] |
| M-fit | 0.960 [0.952, 0.967] |
| D-noisyor | 0.906 [0.894, 0.918] |
| D-fit | 0.994 [0.991, 0.996] |
| MD-fit | 0.996 [0.995, 0.998] |

## ece

| arm | EN |
|---|---|
| B-raw | 0.091 [0.079, 0.109] |
| B-fit | 0.035 [0.029, 0.055] |
| M-raw | 0.061 [0.056, 0.077] |
| M-fit | 0.017 [0.018, 0.036] |
| D-noisyor | 0.242 [0.224, 0.261] |
| D-fit | 0.013 [0.010, 0.022] |
| MD-fit | 0.018 [0.015, 0.025] |

## brier

| arm | EN |
|---|---|
| B-raw | 0.160 [0.152, 0.169] |
| B-fit | 0.150 [0.142, 0.159] |
| M-raw | 0.082 [0.075, 0.088] |
| M-fit | 0.078 [0.071, 0.086] |
| D-noisyor | 0.222 [0.206, 0.239] |
| D-fit | 0.028 [0.022, 0.034] |
| MD-fit | 0.020 [0.016, 0.025] |

ECE bootstrap intervals are biased upward (resampling adds binning noise); compare point estimates and the paired differences below.

## Effects (paired bootstrap, 95% CI)

| comparison | metric | EN |
|---|---|---|
| M-raw − B-raw | accuracy | +0.111 [+0.092, +0.131] |
| M-raw − B-raw | auc | +0.101 [+0.088, +0.113] |
| M-raw − B-raw | ece | -0.030 [-0.042, -0.011] |
| D-fit − B-fit | accuracy | +0.185 [+0.165, +0.206] |
| D-fit − B-fit | auc | +0.136 [+0.120, +0.153] |
| D-fit − B-fit | ece | -0.023 [-0.042, -0.011] |
| D-noisyor − M-raw | accuracy | -0.134 [-0.155, -0.115] |
| D-noisyor − M-raw | auc | -0.053 [-0.066, -0.040] |
| D-noisyor − M-raw | ece | +0.182 [+0.154, +0.197] |
| D-fit − M-fit | accuracy | +0.075 [+0.059, +0.089] |
| D-fit − M-fit | auc | +0.034 [+0.026, +0.042] |
| D-fit − M-fit | ece | -0.004 [-0.021, -0.000] |
| MD-fit − M-fit | accuracy | +0.085 [+0.072, +0.099] |
| MD-fit − M-fit | auc | +0.037 [+0.030, +0.044] |
| MD-fit − M-fit | ece | +0.001 [-0.016, +0.003] |
