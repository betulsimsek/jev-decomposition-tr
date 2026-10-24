"""Jev vs Decisions on the same items: paired bootstrap of decisions − jev, per arm."""

import sys

from analyze import METRICS, RESULTS, load, paired_diff
from compare import ARMS, predictions
from questions import TASKS

task = sys.argv[1] if len(sys.argv) > 1 else "offense"
lines = [f"# Jev vs Decisions, same items ({task})\n",
         "| arm | lang | metric | jev | decisions | decisions − jev [95% CI] |", "|---|---|---|---|---|---|"]
for lang in TASKS[task]["langs"]:
    j, d = load(lang, RESULTS, task), load(lang, RESULTS / "decisions", task)
    ids = sorted(set(j["id"]) & set(d["id"]))
    j, d = (x[x["id"].isin(ids)].sort_values("id").reset_index(drop=True) for x in (j, d))
    assert (j["label"] == d["label"]).all()
    y, pj, pd_ = j["label"].to_numpy(), predictions(j, task), predictions(d, task)
    for arm in ARMS:
        for name in ["accuracy", "auc", "ece"]:
            fn = METRICS[name]
            diff, lo, hi = paired_diff(y, pj[arm], pd_[arm], fn)
            star = "" if lo <= 0 <= hi else "*"
            lines.append(f"| {arm} | {lang.upper()} | {name} | {fn(y, pj[arm]):.3f} | {fn(y, pd_[arm]):.3f} | {diff:+.3f}{star} [{lo:+.3f}, {hi:+.3f}] |")
out = RESULTS / TASKS[task]["subdir"] / "jev_vs_decisions.md"
out.write_text("\n".join(lines) + "\n\n`*` = 95% CI excludes zero.\n")
print("\n".join(lines))
