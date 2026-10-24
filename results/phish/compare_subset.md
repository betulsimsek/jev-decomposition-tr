# Backend comparison (jev, laya, qwen, openjev, decisions, all on the same 500 items of qwen)

## accuracy

| arm | jev EN | laya EN | qwen EN | openjev EN | decisions EN |
|---|---|---|---|---|---|
| B-raw | 0.600 | 0.600 | 0.638 | 0.500 | 0.782 |
| M-raw | 0.888 | 0.726 | 0.624 | 0.488 | 0.904 |
| D-noisyor | 0.802 | 0.604 | 0.500 | 0.500 | 0.768 |
| M-fit | 0.900 | 0.730 | 0.764 | 0.498 | 0.904 |
| D-fit | 0.944 | 0.910 | 0.936 | 0.822 | 0.962 |

## auc

| arm | jev EN | laya EN | qwen EN | openjev EN | decisions EN |
|---|---|---|---|---|---|
| B-raw | 0.806 | 0.752 | 0.777 | 0.389 | 0.875 |
| M-raw | 0.971 | 0.822 | 0.833 | 0.464 | 0.969 |
| D-noisyor | 0.953 | 0.885 | 0.957 | 0.392 | 0.916 |
| M-fit | 0.971 | 0.821 | 0.830 | 0.510 | 0.968 |
| D-fit | 0.988 | 0.968 | 0.981 | 0.886 | 0.994 |

## ece

| arm | jev EN | laya EN | qwen EN | openjev EN | decisions EN |
|---|---|---|---|---|---|
| B-raw | 0.264 | 0.395 | 0.230 | 0.454 | 0.101 |
| M-raw | 0.137 | 0.171 | 0.207 | 0.188 | 0.072 |
| D-noisyor | 0.264 | 0.328 | 0.471 | 0.439 | 0.230 |
| M-fit | 0.042 | 0.092 | 0.058 | 0.046 | 0.035 |
| D-fit | 0.028 | 0.027 | 0.041 | 0.063 | 0.021 |

## Effects (paired bootstrap, 95% CI)

| comparison | metric | jev EN | laya EN | qwen EN | openjev EN | decisions EN |
|---|---|---|---|---|---|---|
| M-raw − B-raw | accuracy | +0.288* | +0.126* | -0.014 | -0.012 | +0.122* |
| M-raw − B-raw | auc | +0.166* | +0.070* | +0.056* | +0.074* | +0.094* |
| M-raw − B-raw | ece | -0.127* | -0.224* | -0.023 | -0.266* | -0.030 |
| D-fit − B-fit | accuracy | +0.220* | +0.186* | +0.208* | +0.228* | +0.166* |
| D-fit − B-fit | auc | +0.184* | +0.233* | +0.203* | +0.275* | +0.121* |
| D-fit − B-fit | ece | -0.025* | -0.000 | -0.065* | +0.019 | -0.028* |
| D-noisyor − M-raw | accuracy | -0.086* | -0.122* | -0.124* | +0.012* | -0.136* |
| D-noisyor − M-raw | auc | -0.019* | +0.063* | +0.124* | -0.072* | -0.053* |
| D-noisyor − M-raw | ece | +0.127* | +0.157* | +0.264* | +0.251* | +0.158* |
| D-fit − M-fit | accuracy | +0.044* | +0.180* | +0.172* | +0.324* | +0.058* |
| D-fit − M-fit | auc | +0.018* | +0.148* | +0.150* | +0.376* | +0.026* |
| D-fit − M-fit | ece | -0.014 | -0.066* | -0.018 | +0.017 | -0.014 |
| MD-fit − M-fit | accuracy | +0.058* | +0.180* | +0.174* | +0.326* | +0.072* |
| MD-fit − M-fit | auc | +0.020* | +0.147* | +0.152* | +0.387* | +0.028* |
| MD-fit − M-fit | ece | -0.014* | -0.050* | -0.031* | +0.010 | -0.010* |

`*` = 95% CI excludes zero.

## Mean predicted P(phishing) on positive / negative items

| backend | lang | B-raw | M-raw | D-noisyor |
|---|---|---|---|---|
| jev | EN | 0.33 / 0.14 | 0.68 / 0.18 | 0.99 / 0.53 |
| laya | EN | 0.21 / 0.00 | 0.61 / 0.18 | 0.95 / 0.70 |
| qwen | EN | 0.38 / 0.16 | 0.38 / 0.20 | 1.00 / 0.94 |
| openjev | EN | 0.04 / 0.05 | 0.63 / 0.63 | 0.94 / 0.94 |
| decisions | EN | 0.59 / 0.25 | 0.79 / 0.18 | 1.00 / 0.46 |
