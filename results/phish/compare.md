# Backend comparison (jev, laya, openjev)

## accuracy

| arm | jev EN | laya EN | openjev EN |
|---|---|---|---|
| B-raw | 0.599 | 0.610 | 0.500 |
| M-raw | 0.882 | 0.733 | 0.486 |
| D-noisyor | 0.794 | 0.589 | 0.500 |
| M-fit | 0.897 | 0.734 | 0.496 |
| D-fit | 0.952 | 0.897 | 0.824 |

## auc

| arm | jev EN | laya EN | openjev EN |
|---|---|---|---|
| B-raw | 0.811 | 0.754 | 0.368 |
| M-raw | 0.969 | 0.809 | 0.463 |
| D-noisyor | 0.946 | 0.872 | 0.389 |
| M-fit | 0.969 | 0.808 | 0.535 |
| D-fit | 0.989 | 0.959 | 0.894 |

## ece

| arm | jev EN | laya EN | openjev EN |
|---|---|---|---|
| B-raw | 0.261 | 0.388 | 0.454 |
| M-raw | 0.140 | 0.162 | 0.179 |
| D-noisyor | 0.270 | 0.335 | 0.439 |
| M-fit | 0.041 | 0.049 | 0.067 |
| D-fit | 0.016 | 0.023 | 0.057 |

## Effects (paired bootstrap, 95% CI)

| comparison | metric | jev EN | laya EN | openjev EN |
|---|---|---|---|---|
| M-raw − B-raw | accuracy | +0.283* | +0.123* | -0.014 |
| M-raw − B-raw | auc | +0.159* | +0.055* | +0.095* |
| M-raw − B-raw | ece | -0.121* | -0.225* | -0.275* |
| D-fit − B-fit | accuracy | +0.214* | +0.167* | +0.221* |
| D-fit − B-fit | auc | +0.179* | +0.221* | +0.262* |
| D-fit − B-fit | ece | -0.019* | -0.001 | +0.019 |
| D-noisyor − M-raw | accuracy | -0.088* | -0.144* | +0.014* |
| D-noisyor − M-raw | auc | -0.023* | +0.064* | -0.074* |
| D-noisyor − M-raw | ece | +0.130* | +0.172* | +0.261* |
| D-fit − M-fit | accuracy | +0.054* | +0.163* | +0.327* |
| D-fit − M-fit | auc | +0.020* | +0.151* | +0.358* |
| D-fit − M-fit | ece | -0.025* | -0.026* | -0.010 |
| MD-fit − M-fit | accuracy | +0.059* | +0.164* | +0.325* |
| MD-fit − M-fit | auc | +0.023* | +0.152* | +0.364* |
| MD-fit − M-fit | ece | -0.031* | -0.026* | -0.011 |

`*` = 95% CI excludes zero.

## Mean predicted P(phishing) on positive / negative items

| backend | lang | B-raw | M-raw | D-noisyor |
|---|---|---|---|---|
| jev | EN | 0.33 / 0.15 | 0.68 / 0.18 | 0.99 / 0.55 |
| laya | EN | 0.22 / 0.00 | 0.61 / 0.18 | 0.94 / 0.72 |
| openjev | EN | 0.04 / 0.05 | 0.63 / 0.64 | 0.94 / 0.94 |
