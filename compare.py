"""Put every backend side by side: is the decomposition finding a Jev quirk?

Reads the same raw files analyze.py reads (results/ for Jev, results/<backend>/
for the others), skips backends that have not finished both languages, and
writes results/compare.md.
"""

from pathlib import Path

import numpy as np

from analyze import COMPARISONS, LANGS, METRICS, RESULTS, load, paired_diff, predictions

BACKENDS = {"jev": RESULTS, "laya": RESULTS / "laya", "qwen": RESULTS / "qwen"}
ARMS = ["B-raw", "M-raw", "D-noisyor", "M-fit", "D-fit"]
N_POSTS = 1000


def complete(path: Path) -> bool:
    files = [path / f"raw_{lang}{s}.jsonl" for lang in LANGS for s in ("", "_bare")]
    return all(f.exists() and sum(1 for _ in f.open()) == N_POSTS for f in files)


def main() -> None:
    ready = {b: p for b, p in BACKENDS.items() if complete(p)}
    data = {}
    for b, path in ready.items():
        for lang in LANGS:
            df = load(lang, path)
            data[b, lang] = (df["label"].to_numpy(), predictions(df))

    lines = [f"# Backend comparison ({', '.join(ready)})\n"]
    for name in ["accuracy", "auc", "ece"]:
        lines.append(f"## {name}\n")
        head = " | ".join(f"{b} {lang.upper()}" for b in ready for lang in LANGS)
        lines.append(f"| arm | {head} |\n|---|" + "---|" * (2 * len(ready)))
        for arm in ARMS:
            cells = [f"{METRICS[name](*_yp(data[b, lang], arm)):.3f}"
                     for b in ready for lang in LANGS]
            lines.append(f"| {arm} | " + " | ".join(cells) + " |")
        lines.append("")

    lines.append("## Effects (paired bootstrap, 95% CI)\n")
    head = " | ".join(f"{b} {lang.upper()}" for b in ready for lang in LANGS)
    lines.append(f"| comparison | metric | {head} |\n|---|---|" + "---|" * (2 * len(ready)))
    for a, b_arm in COMPARISONS:
        for name in ["accuracy", "auc", "ece"]:
            cells = []
            for b in ready:
                for lang in LANGS:
                    y, p = data[b, lang]
                    d, lo, hi = paired_diff(y, p[a], p[b_arm], METRICS[name])
                    star = "" if lo <= 0 <= hi else "*"
                    cells.append(f"{d:+.3f}{star}")
            lines.append(f"| {b_arm} − {a} | {name} | " + " | ".join(cells) + " |")
    lines.append("\n`*` = 95% CI excludes zero.\n")

    lines.append("## Mean predicted P(offensive) on OFF / NOT posts\n")
    lines.append("| backend | lang | " + " | ".join(ARMS[:3]) + " |\n|---|---|---|---|---|")
    for b in ready:
        for lang in LANGS:
            y, p = data[b, lang]
            cells = [f"{p[arm][y == 1].mean():.2f} / {p[arm][y == 0].mean():.2f}"
                     for arm in ARMS[:3]]
            lines.append(f"| {b} | {lang.upper()} | " + " | ".join(cells) + " |")

    (RESULTS / "compare.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def _yp(item: tuple[np.ndarray, dict], arm: str) -> tuple[np.ndarray, np.ndarray]:
    y, p = item
    return y, p[arm]


if __name__ == "__main__":
    main()
