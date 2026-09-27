"""Compare asked-once vs decomposed questions, per language.

Arms
  B-raw      bare question, no definition ("Is this post offensive?")
  B-fit      bare, Platt-scaled
  M-raw      monolithic Noul probability as returned
  M-fit      monolithic, Platt-scaled on labels (1-feature logistic regression)
  D-noisyor  atomic Nouls combined with noisy-OR, no labels used
  D-fit      logistic regression over the 5 atomic Nouls
  MD-fit     logistic regression over monolithic + atomic (does D add info?)

Fitted arms use 5-fold out-of-fold predictions, so every post is scored by
a model that never saw its label.

Why both raw and fitted arms: fitting weights on labels also recalibrates.
M-fit vs D-fit isolates what decomposition adds beyond fitting; AUC isolates
ranking information from calibration entirely.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from questions import ATOMIC_KEYS

RESULTS = Path("results")
LANGS = ["en", "tr"]
ARMS = ["B-raw", "B-fit", "M-raw", "M-fit", "D-noisyor", "D-fit", "MD-fit"]
COMPARISONS = [
    ("B-raw", "M-raw"),       # adding the definition, no fitting
    ("B-fit", "D-fit"),       # the "asked once vs split + fitted" setup
    ("M-raw", "D-noisyor"),   # splitting without labels
    ("M-fit", "D-fit"),       # splitting, both sides fitted
    ("M-fit", "MD-fit"),      # do atomic answers add info to the definition?
]
N_BOOT = 1000
RNG = np.random.default_rng(0)


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def oof_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    out = np.empty(len(y))
    for train, test in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
        model = LogisticRegression().fit(X[train], y[train])
        out[test] = model.predict_proba(X[test])[:, 1]
    return out


def predictions(df: pd.DataFrame) -> dict[str, np.ndarray]:
    y = df["label"].to_numpy()
    b = df["offensive_bare"].to_numpy()
    m = df["offensive"].to_numpy()
    A = df[ATOMIC_KEYS].to_numpy()
    return {
        "B-raw": b,
        "B-fit": oof_fit(logit(b)[:, None], y),
        "M-raw": m,
        "M-fit": oof_fit(logit(m)[:, None], y),
        "D-noisyor": 1 - np.prod(1 - A, axis=1),
        "D-fit": oof_fit(logit(A), y),
        "MD-fit": oof_fit(logit(np.column_stack([m, A])), y),
    }


def ece(y: np.ndarray, p: np.ndarray, bins: int = 15) -> float:
    idx = np.minimum((p * bins).astype(int), bins - 1)
    total = 0.0
    for b in range(bins):
        mask = idx == b
        if mask.any():
            total += mask.mean() * abs(y[mask].mean() - p[mask].mean())
    return total


METRICS = {
    "accuracy": lambda y, p: ((p >= 0.5) == y).mean(),
    "macro_f1": lambda y, p: f1_score(y, p >= 0.5, average="macro"),
    "auc": roc_auc_score,
    "ece": ece,
    "brier": brier_score_loss,
}


def read_raw(path: Path) -> pd.DataFrame:
    rows = [json.loads(line) for line in path.open()]
    return pd.DataFrame([{"id": r["id"], "label": r["label"], **r["nouls"]} for r in rows])


def load(lang: str, results: Path = RESULTS) -> pd.DataFrame:
    main = read_raw(results / f"raw_{lang}.jsonl")
    bare = read_raw(results / f"raw_{lang}_bare.jsonl")
    df = main.merge(bare, on=["id", "label"], validate="one_to_one")
    assert len(df) == len(main) == len(bare), "main and bare runs cover different posts"
    return df.sort_values("id").reset_index(drop=True)


def boot_ci(y, p, fn) -> tuple[float, float]:
    n = len(y)
    stats = [fn(y[i], p[i]) for i in (RNG.integers(0, n, n) for _ in range(N_BOOT))]
    return tuple(np.percentile(stats, [2.5, 97.5]))


def paired_diff(y, p_a, p_b, fn) -> tuple[float, float, float]:
    """Point estimate and 95% CI of fn(b) - fn(a) on the same resamples."""
    n = len(y)
    diffs = []
    for _ in range(N_BOOT):
        i = RNG.integers(0, n, n)
        diffs.append(fn(y[i], p_b[i]) - fn(y[i], p_a[i]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return fn(y, p_b) - fn(y, p_a), lo, hi


def interaction(ys, preds, a, b, fn) -> tuple[float, float, float]:
    """(effect in TR) - (effect in EN) for arm a -> b; languages resampled independently."""
    def effect(lang, i):
        y = ys[lang][i]
        return fn(y, preds[lang][b][i]) - fn(y, preds[lang][a][i])

    full = {lang: np.arange(len(ys[lang])) for lang in LANGS}
    point = effect("tr", full["tr"]) - effect("en", full["en"])
    diffs = []
    for _ in range(N_BOOT):
        i_tr = RNG.integers(0, len(ys["tr"]), len(ys["tr"]))
        i_en = RNG.integers(0, len(ys["en"]), len(ys["en"]))
        diffs.append(effect("tr", i_tr) - effect("en", i_en))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return point, lo, hi


def reliability_plot(preds: dict, ys: dict, results: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
    edges = np.linspace(0, 1, 11)
    for ax, lang in zip(axes, LANGS):
        ax.plot([0, 1], [0, 1], color="#999", lw=1, ls="--")
        for arm in ["B-raw", "M-raw", "D-noisyor", "D-fit"]:
            p, y = preds[lang][arm], ys[lang]
            idx = np.minimum(np.digitize(p, edges) - 1, 9)
            xs, fs = [], []
            for b in range(10):
                mask = idx == b
                if mask.sum() >= 10:
                    xs.append(p[mask].mean())
                    fs.append(y[mask].mean())
            ax.plot(xs, fs, marker="o", ms=4, label=arm)
        ax.set_title({"en": "English (OLID)", "tr": "Turkish (OffensEval-TR)"}[lang])
        ax.set_xlabel("predicted P(offensive)")
    axes[0].set_ylabel("observed fraction offensive")
    axes[1].legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig(results / "reliability.png", dpi=160)


def main(results: Path = RESULTS) -> None:
    rows, preds, ys = [], {}, {}
    for lang in LANGS:
        df = load(lang, results)
        ys[lang] = df["label"].to_numpy()
        preds[lang] = predictions(df)
        for arm, p in preds[lang].items():
            for name, fn in METRICS.items():
                lo, hi = boot_ci(ys[lang], p, fn)
                rows.append(
                    dict(lang=lang, arm=arm, metric=name,
                         value=fn(ys[lang], p), lo=lo, hi=hi, n=len(df))
                )
    metrics = pd.DataFrame(rows)
    metrics.to_csv(results / "metrics.csv", index=False)

    lines = ["# Results\n"]
    for name in METRICS:
        table = metrics[metrics.metric == name].pivot(index="arm", columns="lang")
        lines.append(f"## {name}\n")
        lines.append("| arm | EN | TR |\n|---|---|---|")
        for arm in ARMS:
            cells = []
            for lang in LANGS:
                v, lo, hi = (table.loc[arm, (c, lang)] for c in ("value", "lo", "hi"))
                cells.append(f"{v:.3f} [{lo:.3f}, {hi:.3f}]")
            lines.append(f"| {arm} | " + " | ".join(cells) + " |")
        lines.append("")

    lines.append(
        "ECE bootstrap intervals are biased upward (resampling adds binning "
        "noise); compare point estimates and the paired differences below.\n"
    )
    lines.append("## Effects (paired bootstrap, 95% CI)\n")
    lines.append("| comparison | metric | EN | TR | TR − EN |\n|---|---|---|---|---|")
    for a, b in COMPARISONS:
        for name in ["accuracy", "auc", "ece"]:
            cells = []
            for lang in LANGS:
                d, lo, hi = paired_diff(ys[lang], preds[lang][a], preds[lang][b], METRICS[name])
                cells.append(f"{d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            d, lo, hi = interaction(ys, preds, a, b, METRICS[name])
            cells.append(f"{d:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            lines.append(f"| {b} − {a} | {name} | " + " | ".join(cells) + " |")
    (results / "summary.md").write_text("\n".join(lines) + "\n")
    reliability_plot(preds, ys, results)
    print("\n".join(lines))


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["jev", "laya", "qwen"], default="jev",
                   help="jev reads results/, others read results/<backend>/")
    backend = p.parse_args().backend
    main(RESULTS if backend == "jev" else RESULTS / backend)
