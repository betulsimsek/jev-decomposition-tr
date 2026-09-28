"""Score every sampled post with Laya, locally, using the same questions as Jev.

Both languages go to the `multilingual` checkpoint, so as with Jev one model
sees both languages and text language stays the only variable.

Writes results/laya/raw_<lang>.jsonl and raw_<lang>_bare.jsonl in the same
format as run.py, so analyze.py reads them unchanged. Laya is deterministic
and fast (about 0.2 s per post on an M3), so there is no resume logic: a
rerun overwrites.
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from laya import Router
from tqdm import tqdm

from questions import TASKS, state_of

CHECKPOINT = "multilingual"
OUT = Path("results/laya")


def to_laya(questions: dict) -> dict:
    return {
        k: {"type": "noul", "instructions": q.instructions,
            **({"criteria": dict(q.criteria)} if q.criteria else {})}
        for k, q in questions.items()
    }


def run(router: Router, task: str, lang: str, qset: str, batch: int) -> None:
    spec = TASKS[task]
    questions = to_laya(spec["sets"][qset])
    sample = pd.read_csv(spec["data"].format(lang=lang), dtype={"id": str})
    suffix = "" if qset == "main" else f"_{qset}"
    out = OUT / spec["subdir"] / f"raw_{lang}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for start in tqdm(range(0, len(sample), batch), desc=f"{lang} {qset}"):
            rows = sample.iloc[start:start + batch]
            results = router.predict_batch([
                {"state": state_of(task, text), "questions": questions, "model": CHECKPOINT}
                for text in rows.text
            ])
            for row, res in zip(rows.itertuples(), results):
                record = {
                    "id": row.id,
                    "label": int(row.label),
                    "model": f"laya-{CHECKPOINT}",
                    "nouls": {k: v["noul"] for k, v in res["answers"].items()},
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--task", choices=list(TASKS), default="offense")
    args = p.parse_args()
    router = Router()
    for lang in TASKS[args.task]["langs"]:
        for qset in TASKS[args.task]["sets"]:
            run(router, args.task, lang, qset, args.batch)
