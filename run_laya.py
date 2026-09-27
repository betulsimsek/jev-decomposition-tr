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

from questions import QUESTION_SETS

CHECKPOINT = "multilingual"
OUT = Path("results/laya")


def to_laya(questions: dict) -> dict:
    return {
        k: {"type": "noul", "instructions": q.instructions,
            **({"criteria": dict(q.criteria)} if q.criteria else {})}
        for k, q in questions.items()
    }


def run(router: Router, lang: str, qset: str, batch: int) -> None:
    questions = to_laya(QUESTION_SETS[qset])
    sample = pd.read_csv(f"data/sample_{lang}.csv", dtype={"id": str})
    suffix = "" if qset == "main" else f"_{qset}"
    with (OUT / f"raw_{lang}{suffix}.jsonl").open("w") as f:
        for start in tqdm(range(0, len(sample), batch), desc=f"{lang} {qset}"):
            rows = sample.iloc[start:start + batch]
            results = router.predict_batch([
                {"state": {"post": text}, "questions": questions, "model": CHECKPOINT}
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
    args = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    router = Router()
    for lang in ["en", "tr"]:
        for qset in QUESTION_SETS:
            run(router, lang, qset, args.batch)
