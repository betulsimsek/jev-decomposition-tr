"""Put every backend side by side: is the decomposition finding a Jev quirk?

Reads the same raw files analyze.py reads (results/ for Jev, results/<backend>/
for the others), skips backends that have not finished both languages, and
writes results/[<task>/]compare.md.

--subset-of <backend> cuts every backend to that backend's items (Qwen ran
only a 500-email phishing subset) and refits the fitted arms on that subset,
so all backends are compared on the same items; writes compare_subset.md.
"""

from pathlib import Path

import numpy as np

from analyze import COMPARISONS, METRICS, POSITIVE, RESULTS, load, paired_diff, predictions
from questions import TASKS

BACKENDS = {"jev": RESULTS, "laya": RESULTS / "laya", "qwen": RESULTS / "qwen",
            "openjev": RESULTS / "openjev", "decisions": RESULTS / "decisions"}
ARMS = ["B-raw", "M-raw", "D-noisyor", "M-fit", "D-fit"]
N_ITEMS = {"offense": 1000, "phish": 2000}


def counts(path: Path, task: str) -> list[int]:
    spec = TASKS[task]
    files = [path / spec["subdir"] / f"raw_{lang}{s}.jsonl" for lang in spec["langs"] for s in ("", "_bare")]
    return [sum(1 for _ in f.open()) if f.exists() else 0 for f in files]


def complete(path: Path, task: str, full: bool = True) -> bool:
    n = counts(path, task)
    return len(set(n)) == 1 and n[0] > 0 and (not full or n[0] == N_ITEMS[task])


def main(task: str = "offense", subset_of: str | None = None) -> None:
    LANGS = TASKS[task]["langs"]
    ready = {b: p for b, p in BACKENDS.items() if complete(p, task, full=subset_of is None)}
    ids = None
    if subset_of:
        ids = {lang: set(load(lang, ready[subset_of], task)["id"]) for lang in LANGS}
    data = {}
    for b, path in ready.items():
        for lang in LANGS:
            df = load(lang, path, task)
            if ids:
                df = df[df["id"].isin(ids[lang])].reset_index(drop=True)
                assert len(df) == len(ids[lang]), (b, lang, len(df))
            data[b, lang] = (df["label"].to_numpy(), predictions(df, task))

    n = len(next(iter(data.values()))[0])
    scope = f", all on the same {n} items of {subset_of}" if subset_of else ""
    lines = [f"# Backend comparison ({', '.join(ready)}{scope})\n"]
    for name in ["accuracy", "auc", "ece"]:
        lines.append(f"## {name}\n")
        head = " | ".join(f"{b} {lang.upper()}" for b in ready for lang in LANGS)
        lines.append(f"| arm | {head} |\n|---|" + "---|" * (len(LANGS) * len(ready)))
        for arm in ARMS:
            cells = [f"{METRICS[name](*_yp(data[b, lang], arm)):.3f}"
                     for b in ready for lang in LANGS]
            lines.append(f"| {arm} | " + " | ".join(cells) + " |")
        lines.append("")

    lines.append("## Effects (paired bootstrap, 95% CI)\n")
    head = " | ".join(f"{b} {lang.upper()}" for b in ready for lang in LANGS)
    lines.append(f"| comparison | metric | {head} |\n|---|---|" + "---|" * (len(LANGS) * len(ready)))
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

    lines.append(f"## Mean predicted P({POSITIVE[task]}) on positive / negative items\n")
    lines.append("| backend | lang | " + " | ".join(ARMS[:3]) + " |\n|---|---|---|---|---|")
    for b in ready:
        for lang in LANGS:
            y, p = data[b, lang]
            cells = [f"{p[arm][y == 1].mean():.2f} / {p[arm][y == 0].mean():.2f}"
                     for arm in ARMS[:3]]
            lines.append(f"| {b} | {lang.upper()} | " + " | ".join(cells) + " |")

    name = "compare_subset.md" if subset_of else "compare.md"
    (RESULTS / TASKS[task]["subdir"] / name).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def _yp(item: tuple[np.ndarray, dict], arm: str) -> tuple[np.ndarray, np.ndarray]:
    y, p = item
    return y, p[arm]


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=list(TASKS), default="offense")
    p.add_argument("--subset-of", choices=list(BACKENDS), help="compare on this backend's items only")
    args = p.parse_args()
    main(args.task, args.subset_of)
