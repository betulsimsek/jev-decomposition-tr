"""Score every sampled post with OpenJev, a second open encoder (DeBERTa-v3-large).

Phase 3 asks whether Laya's timidity is an encoder trait or a Laya trait, so
this needs a decision model that is an encoder, was trained by someone else,
and takes the same instructions + yes/no shape as Jev.

Two deviations from the other backends, both forced by the model:
- OpenJev packs every question into one sequence, so answers could see each
  other. Each question is sent on its own to keep them independent, as with
  Jev and Laya.
- A noul's options are fixed to (no, yes), so the one question with criteria
  ("veiled") gets them appended to its instructions.

The model is English-only (DeBERTa-v3 tokenizer). Turkish is scored too, but
only the English numbers answer the Phase 3 question.

The model code ships inside the model repo (typed_decisions/), not on PyPI;
it is imported from the downloaded snapshot. Writes results/openjev/.
"""

import json
import sys
from pathlib import Path

import pandas as pd
from huggingface_hub import snapshot_download
from tqdm import tqdm

from questions import QUESTION_SETS

REPO = "com-kotobalabs/open-jev-deberta-v3-large"
OUT = Path("results/openjev")


def instructions(q) -> str:
    if not q.criteria:
        return q.instructions
    return f"{q.instructions} Yes: {q.criteria['true']}. No: {q.criteria['false']}."


def run(model, lang: str, qset: str) -> None:
    questions = {k: instructions(q) for k, q in QUESTION_SETS[qset].items()}
    sample = pd.read_csv(f"data/sample_{lang}.csv", dtype={"id": str})
    suffix = "" if qset == "main" else f"_{qset}"
    with (OUT / f"raw_{lang}{suffix}.jsonl").open("w") as f:
        for row in tqdm(list(sample.itertuples()), desc=f"{lang} {qset}"):
            nouls = {k: model.decide(row.text, [{"type": "noul", "instructions": text}])[0]["noul"]
                     for k, text in questions.items()}
            record = {"id": row.id, "label": int(row.label), "model": REPO, "nouls": nouls}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    path = snapshot_download(REPO)
    sys.path.insert(0, path)
    from typed_decisions.open_jev import OpenJev

    OUT.mkdir(parents=True, exist_ok=True)
    model = OpenJev.from_pretrained(path)
    for lang in ["en", "tr"]:
        for qset in QUESTION_SETS:
            run(model, lang, qset)
