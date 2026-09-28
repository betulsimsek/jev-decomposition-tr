# Results

## accuracy

| arm | EN |
|---|---|
| B-raw | 0.500 [0.477, 0.521] |
| B-fit | 0.603 [0.582, 0.625] |
| M-raw | 0.486 [0.465, 0.509] |
| M-fit | 0.496 [0.475, 0.518] |
| D-noisyor | 0.500 [0.477, 0.521] |
| D-fit | 0.824 [0.807, 0.840] |
| MD-fit | 0.822 [0.804, 0.839] |

## macro_f1

| arm | EN |
|---|---|
| B-raw | 0.333 [0.323, 0.343] |
| B-fit | 0.603 [0.581, 0.623] |
| M-raw | 0.330 [0.319, 0.342] |
| M-fit | 0.496 [0.475, 0.519] |
| D-noisyor | 0.333 [0.323, 0.342] |
| D-fit | 0.823 [0.806, 0.840] |
| MD-fit | 0.822 [0.805, 0.838] |

## auc

| arm | EN |
|---|---|
| B-raw | 0.368 [0.342, 0.392] |
| B-fit | 0.632 [0.607, 0.655] |
| M-raw | 0.463 [0.436, 0.488] |
| M-fit | 0.535 [0.510, 0.562] |
| D-noisyor | 0.389 [0.364, 0.414] |
| D-fit | 0.894 [0.880, 0.908] |
| MD-fit | 0.899 [0.885, 0.913] |

## ece

| arm | EN |
|---|---|
| B-raw | 0.454 [0.433, 0.477] |
| B-fit | 0.038 [0.026, 0.061] |
| M-raw | 0.179 [0.157, 0.199] |
| M-fit | 0.067 [0.046, 0.088] |
| D-noisyor | 0.439 [0.417, 0.463] |
| D-fit | 0.057 [0.047, 0.076] |
| MD-fit | 0.056 [0.045, 0.073] |

## brier

| arm | EN |
|---|---|
| B-raw | 0.458 [0.439, 0.477] |
| B-fit | 0.238 [0.234, 0.243] |
| M-raw | 0.276 [0.269, 0.282] |
| M-fit | 0.249 [0.248, 0.250] |
| D-noisyor | 0.447 [0.425, 0.467] |
| D-fit | 0.126 [0.118, 0.135] |
| MD-fit | 0.124 [0.115, 0.133] |

ECE bootstrap intervals are biased upward (resampling adds binning noise); compare point estimates and the paired differences below.

## Effects (paired bootstrap, 95% CI)

| comparison | metric | EN |
|---|---|---|
| M-raw − B-raw | accuracy | -0.014 [-0.054, +0.028] |
| M-raw − B-raw | auc | +0.095 [+0.068, +0.121] |
| M-raw − B-raw | ece | -0.275 [-0.316, -0.232] |
| D-fit − B-fit | accuracy | +0.221 [+0.192, +0.249] |
| D-fit − B-fit | auc | +0.262 [+0.233, +0.292] |
| D-fit − B-fit | ece | +0.019 [-0.004, +0.040] |
| D-noisyor − M-raw | accuracy | +0.014 [+0.008, +0.020] |
| D-noisyor − M-raw | auc | -0.074 [-0.107, -0.040] |
| D-noisyor − M-raw | ece | +0.261 [+0.251, +0.271] |
| D-fit − M-fit | accuracy | +0.327 [+0.302, +0.351] |
| D-fit − M-fit | auc | +0.358 [+0.330, +0.385] |
| D-fit − M-fit | ece | -0.010 [-0.030, +0.022] |
| MD-fit − M-fit | accuracy | +0.325 [+0.298, +0.351] |
| MD-fit − M-fit | auc | +0.364 [+0.338, +0.390] |
| MD-fit − M-fit | ece | -0.011 [-0.032, +0.018] |
