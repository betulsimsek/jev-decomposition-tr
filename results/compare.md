# Backend comparison (jev, laya)

## accuracy

| arm | jev EN | jev TR | laya EN | laya TR |
|---|---|---|---|---|
| B-raw | 0.693 | 0.813 | 0.724 | 0.679 |
| M-raw | 0.738 | 0.828 | 0.614 | 0.602 |
| D-noisyor | 0.615 | 0.726 | 0.762 | 0.681 |
| M-fit | 0.735 | 0.843 | 0.738 | 0.667 |
| D-fit | 0.759 | 0.836 | 0.764 | 0.691 |

## auc

| arm | jev EN | jev TR | laya EN | laya TR |
|---|---|---|---|---|
| B-raw | 0.775 | 0.904 | 0.813 | 0.725 |
| M-raw | 0.819 | 0.921 | 0.797 | 0.733 |
| D-noisyor | 0.749 | 0.898 | 0.829 | 0.742 |
| M-fit | 0.818 | 0.920 | 0.796 | 0.733 |
| D-fit | 0.827 | 0.914 | 0.835 | 0.756 |

## ece

| arm | jev EN | jev TR | laya EN | laya TR |
|---|---|---|---|---|
| B-raw | 0.073 | 0.064 | 0.149 | 0.189 |
| M-raw | 0.087 | 0.061 | 0.291 | 0.266 |
| D-noisyor | 0.306 | 0.233 | 0.090 | 0.152 |
| M-fit | 0.035 | 0.026 | 0.042 | 0.069 |
| D-fit | 0.046 | 0.025 | 0.028 | 0.056 |

## Effects (paired bootstrap, 95% CI)

| comparison | metric | jev EN | jev TR | laya EN | laya TR |
|---|---|---|---|---|---|
| M-raw − B-raw | accuracy | +0.045* | +0.015 | -0.110* | -0.077* |
| M-raw − B-raw | auc | +0.044* | +0.016* | -0.016* | +0.008 |
| M-raw − B-raw | ece | +0.014 | -0.003 | +0.142* | +0.077* |
| D-fit − B-fit | accuracy | +0.059* | +0.019 | +0.008 | +0.017 |
| D-fit − B-fit | auc | +0.052* | +0.010 | +0.022* | +0.032* |
| D-fit − B-fit | ece | +0.009 | -0.003 | -0.014 | -0.014 |
| D-noisyor − M-raw | accuracy | -0.123* | -0.102* | +0.148* | +0.079* |
| D-noisyor − M-raw | auc | -0.070* | -0.023* | +0.032* | +0.009 |
| D-noisyor − M-raw | ece | +0.219* | +0.172* | -0.201* | -0.115* |
| D-fit − M-fit | accuracy | +0.024* | -0.007 | +0.026* | +0.024 |
| D-fit − M-fit | auc | +0.009 | -0.007 | +0.039* | +0.023* |
| D-fit − M-fit | ece | +0.011 | -0.002 | -0.014 | -0.013 |
| MD-fit − M-fit | accuracy | +0.026* | +0.004 | +0.030* | +0.018 |
| MD-fit − M-fit | auc | +0.019* | +0.002 | +0.037* | +0.022* |
| MD-fit − M-fit | ece | -0.003 | +0.002 | -0.012 | -0.025 |

`*` = 95% CI excludes zero.

## Mean predicted P(offensive) on OFF / NOT posts

| backend | lang | B-raw | M-raw | D-noisyor |
|---|---|---|---|---|
| jev | EN | 0.65 / 0.37 | 0.71 / 0.33 | 0.91 / 0.70 |
| jev | TR | 0.68 / 0.21 | 0.70 / 0.18 | 0.93 / 0.54 |
| laya | EN | 0.55 / 0.19 | 0.32 / 0.10 | 0.71 / 0.29 |
| laya | TR | 0.57 / 0.28 | 0.36 / 0.17 | 0.70 / 0.40 |
