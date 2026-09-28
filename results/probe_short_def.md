# Probe: short one-sentence definition (exploratory)

Short definition: *Is this post offensive, i.e. does it contain profanity or a targeted insult or threat?*

| backend | lang | arm | accuracy | AUC | ECE | mean P on OFF / NOT |
|---|---|---|---|---|---|---|
| laya | EN | bare | 0.724 | 0.813 | 0.149 | 0.55 / 0.19 |
| laya | EN | full definition | 0.614 | 0.797 | 0.291 | 0.32 / 0.10 |
| laya | EN | short definition | 0.656 | 0.819 | 0.266 | 0.38 / 0.10 |
| laya | TR | bare | 0.679 | 0.725 | 0.189 | 0.57 / 0.28 |
| laya | TR | full definition | 0.602 | 0.733 | 0.266 | 0.36 / 0.17 |
| laya | TR | short definition | 0.601 | 0.743 | 0.288 | 0.35 / 0.15 |
| openjev | EN | bare | 0.666 | 0.726 | 0.111 | 0.70 / 0.47 |
| openjev | EN | full definition | 0.552 | 0.709 | 0.328 | 0.88 / 0.77 |
| openjev | EN | short definition | 0.643 | 0.717 | 0.078 | 0.55 / 0.36 |

## Short definition vs bare (paired bootstrap, `*` = 95% CI excludes zero)

| backend | lang | accuracy | AUC | ECE |
|---|---|---|---|---|
| laya | EN | -0.068* | +0.006 | +0.118* |
| laya | TR | -0.078* | +0.018* | +0.098* |
| openjev | EN | -0.023 | -0.009 | -0.033* |
