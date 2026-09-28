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

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from huggingface_hub import snapshot_download
from tqdm import tqdm

from questions import TASKS, state_of

REPO = "com-kotobalabs/open-jev-deberta-v3-large"
OUT = Path("results/openjev")


def instructions(q) -> str:
    if not q.criteria:
        return q.instructions
    return f"{q.instructions} Yes: {q.criteria['true']}. No: {q.criteria['false']}."


def state_text(task: str, text: str) -> str:
    # OpenJev takes a string state: the raw post, or the email object as JSON
    return text if task == "offense" else json.dumps(state_of(task, text), ensure_ascii=False)


def run(model, task: str, lang: str, qset: str) -> None:
    spec = TASKS[task]
    questions = {k: instructions(q) for k, q in spec["sets"][qset].items()}
    sample = pd.read_csv(spec["data"].format(lang=lang), dtype={"id": str})
    suffix = "" if qset == "main" else f"_{qset}"
    out = OUT / spec["subdir"] / f"raw_{lang}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for row in tqdm(list(sample.itertuples()), desc=f"{lang} {qset}"):
            state = state_text(task, row.text)
            nouls = {k: model.decide(state, [{"type": "noul", "instructions": text}])[0]["noul"]
                     for k, text in questions.items()}
            record = {"id": row.id, "label": int(row.label), "model": REPO, "nouls": nouls}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=list(TASKS), default="offense")
    args = p.parse_args()
    path = snapshot_download(REPO)
    sys.path.insert(0, path)
    from typed_decisions.open_jev import OpenJev

    model = OpenJev.from_pretrained(path)
    for lang in TASKS[args.task]["langs"]:
        for qset in TASKS[args.task]["sets"]:
            run(model, args.task, lang, qset)
