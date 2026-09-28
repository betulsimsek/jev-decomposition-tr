# Results

## accuracy

| arm | EN |
|---|---|
| B-raw | 0.610 [0.588, 0.630] |
| B-fit | 0.730 [0.711, 0.751] |
| M-raw | 0.733 [0.714, 0.751] |
| M-fit | 0.734 [0.716, 0.752] |
| D-noisyor | 0.589 [0.568, 0.610] |
| D-fit | 0.897 [0.884, 0.909] |
| MD-fit | 0.898 [0.885, 0.911] |

## macro_f1

| arm | EN |
|---|---|
| B-raw | 0.539 [0.518, 0.562] |
| B-fit | 0.718 [0.699, 0.738] |
| M-raw | 0.729 [0.708, 0.748] |
| M-fit | 0.734 [0.713, 0.751] |
| D-noisyor | 0.519 [0.495, 0.541] |
| D-fit | 0.897 [0.884, 0.909] |
| MD-fit | 0.898 [0.885, 0.911] |

## auc

| arm | EN |
|---|---|
| B-raw | 0.754 [0.735, 0.771] |
| B-fit | 0.738 [0.714, 0.759] |
| M-raw | 0.809 [0.790, 0.828] |
| M-fit | 0.808 [0.789, 0.827] |
| D-noisyor | 0.872 [0.858, 0.887] |
| D-fit | 0.959 [0.951, 0.968] |
| MD-fit | 0.961 [0.952, 0.968] |

## ece

| arm | EN |
|---|---|
| B-raw | 0.388 [0.366, 0.408] |
| B-fit | 0.023 [0.016, 0.045] |
| M-raw | 0.162 [0.146, 0.182] |
| M-fit | 0.049 [0.043, 0.073] |
| D-noisyor | 0.335 [0.316, 0.355] |
| D-fit | 0.023 [0.021, 0.039] |
| MD-fit | 0.023 [0.020, 0.040] |

## brier

| arm | EN |
|---|---|
| B-raw | 0.371 [0.352, 0.390] |
| B-fit | 0.181 [0.173, 0.188] |
| M-raw | 0.208 [0.192, 0.222] |
| M-fit | 0.176 [0.167, 0.185] |
| D-noisyor | 0.304 [0.288, 0.320] |
| D-fit | 0.075 [0.066, 0.084] |
| MD-fit | 0.074 [0.067, 0.083] |

ECE bootstrap intervals are biased upward (resampling adds binning noise); compare point estimates and the paired differences below.

## Effects (paired bootstrap, 95% CI)

| comparison | metric | EN |
|---|---|---|
| M-raw − B-raw | accuracy | +0.123 [+0.100, +0.147] |
| M-raw − B-raw | auc | +0.055 [+0.034, +0.076] |
| M-raw − B-raw | ece | -0.225 [-0.244, -0.199] |
| D-fit − B-fit | accuracy | +0.167 [+0.145, +0.190] |
| D-fit − B-fit | auc | +0.221 [+0.198, +0.245] |
| D-fit − B-fit | ece | -0.001 [-0.018, +0.016] |
| D-noisyor − M-raw | accuracy | -0.144 [-0.174, -0.114] |
| D-noisyor − M-raw | auc | +0.064 [+0.046, +0.081] |
| D-noisyor − M-raw | ece | +0.172 [+0.142, +0.198] |
| D-fit − M-fit | accuracy | +0.163 [+0.142, +0.185] |
| D-fit − M-fit | auc | +0.151 [+0.133, +0.170] |
| D-fit − M-fit | ece | -0.026 [-0.043, -0.008] |
| MD-fit − M-fit | accuracy | +0.164 [+0.143, +0.183] |
| MD-fit − M-fit | auc | +0.152 [+0.134, +0.169] |
| MD-fit − M-fit | ece | -0.026 [-0.045, -0.010] |
