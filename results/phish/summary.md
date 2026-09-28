# Results

## accuracy

| arm | EN |
|---|---|
| B-raw | 0.599 [0.578, 0.621] |
| B-fit | 0.738 [0.718, 0.756] |
| M-raw | 0.882 [0.868, 0.897] |
| M-fit | 0.897 [0.884, 0.911] |
| D-noisyor | 0.794 [0.776, 0.811] |
| D-fit | 0.952 [0.943, 0.962] |
| MD-fit | 0.957 [0.949, 0.966] |

## macro_f1

| arm | EN |
|---|---|
| B-raw | 0.523 [0.501, 0.543] |
| B-fit | 0.737 [0.717, 0.755] |
| M-raw | 0.882 [0.867, 0.896] |
| M-fit | 0.897 [0.884, 0.910] |
| D-noisyor | 0.786 [0.767, 0.803] |
| D-fit | 0.952 [0.942, 0.961] |
| MD-fit | 0.957 [0.948, 0.966] |

## auc

| arm | EN |
|---|---|
| B-raw | 0.811 [0.792, 0.828] |
| B-fit | 0.810 [0.792, 0.828] |
| M-raw | 0.969 [0.963, 0.975] |
| M-fit | 0.969 [0.963, 0.975] |
| D-noisyor | 0.946 [0.937, 0.956] |
| D-fit | 0.989 [0.986, 0.992] |
| MD-fit | 0.992 [0.989, 0.995] |

## ece

| arm | EN |
|---|---|
| B-raw | 0.261 [0.242, 0.281] |
| B-fit | 0.035 [0.031, 0.060] |
| M-raw | 0.140 [0.131, 0.154] |
| M-fit | 0.041 [0.033, 0.054] |
| D-noisyor | 0.270 [0.254, 0.287] |
| D-fit | 0.016 [0.013, 0.026] |
| MD-fit | 0.010 [0.010, 0.022] |

## brier

| arm | EN |
|---|---|
| B-raw | 0.258 [0.246, 0.271] |
| B-fit | 0.175 [0.166, 0.183] |
| M-raw | 0.095 [0.089, 0.101] |
| M-fit | 0.072 [0.065, 0.080] |
| D-noisyor | 0.209 [0.194, 0.225] |
| D-fit | 0.036 [0.030, 0.043] |
| MD-fit | 0.031 [0.025, 0.036] |

ECE bootstrap intervals are biased upward (resampling adds binning noise); compare point estimates and the paired differences below.

## Effects (paired bootstrap, 95% CI)

| comparison | metric | EN |
|---|---|---|
| M-raw − B-raw | accuracy | +0.283 [+0.261, +0.304] |
| M-raw − B-raw | auc | +0.159 [+0.142, +0.176] |
| M-raw − B-raw | ece | -0.121 [-0.135, -0.103] |
| D-fit − B-fit | accuracy | +0.214 [+0.194, +0.236] |
| D-fit − B-fit | auc | +0.179 [+0.160, +0.198] |
| D-fit − B-fit | ece | -0.019 [-0.042, -0.011] |
| D-noisyor − M-raw | accuracy | -0.088 [-0.111, -0.066] |
| D-noisyor − M-raw | auc | -0.023 [-0.031, -0.015] |
| D-noisyor − M-raw | ece | +0.130 [+0.106, +0.152] |
| D-fit − M-fit | accuracy | +0.054 [+0.040, +0.070] |
| D-fit − M-fit | auc | +0.020 [+0.014, +0.026] |
| D-fit − M-fit | ece | -0.025 [-0.036, -0.011] |
| MD-fit − M-fit | accuracy | +0.059 [+0.046, +0.074] |
| MD-fit − M-fit | auc | +0.023 [+0.018, +0.028] |
| MD-fit − M-fit | ece | -0.031 [-0.039, -0.017] |
