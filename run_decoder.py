"""Turn a small local decoder LLM into a Noul scorer with the logprob trick.

Same recipe as Privatemode's "System One from GLM Flash" post: put the state,
the question and numbered options in the prompt, prefill the assistant turn
with "choice_index: ", run one forward pass and read the logits of the option
index tokens, renormalised over the options. No sampling, no parsing.

GLM-5.3-Flash needs ~200 GB of RAM, so this uses Qwen3.5-9B (4-bit, MLX) on
the laptop instead: the question is decoder vs encoder vs Jev, not GLM itself.
Options are always 0 = no, 1 = yes; order bias is not averaged out.

Writes results/qwen/raw_<lang>.jsonl and raw_<lang>_bare.jsonl in the same
format as run.py. Re-running skips posts already written.
"""

import argparse
import json
from pathlib import Path

import mlx.core as mx
import pandas as pd
from mlx_lm import load
from tqdm import tqdm

from questions import QUESTION_SETS

MODEL = "mlx-community/Qwen3.5-9B-MLX-4bit"
OUT = Path("results/qwen")
SYSTEM = (
    "You answer a question about a piece of state by choosing one option. "
    "Reply with the index of the correct option only."
)


def prompt(tok, post: str, question) -> str:
    yes, no = "yes", "no"
    if question.criteria:
        yes = f"yes: {question.criteria['true']}"
        no = f"no: {question.criteria['false']}"
    body = json.dumps(
        {
            "state": {"post": post},
            "question": question.instructions,
            "options": [{"index": 0, "name": no}, {"index": 1, "name": yes}],
        },
        ensure_ascii=False,
        indent=1,
    )
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": body}]
    head = tok.apply_chat_template(
        msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    return head + "choice_index: "


def option_ids(tok) -> list[int]:
    ids = [tok.encode(d, add_special_tokens=False) for d in ("0", "1")]
    assert all(len(i) == 1 for i in ids), ids
    return [i[0] for i in ids]


def p_yes(model, tok, text: str, ids: list[int]) -> float:
    tokens = mx.array(tok.encode(text, add_special_tokens=False))[None]
    logits = model(tokens)[0, -1]
    pair = logits[mx.array(ids)].astype(mx.float32)
    return mx.softmax(pair).tolist()[1]


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {json.loads(line)["id"] for line in path.open()}


def run(model, tok, lang: str, qset: str, limit: int | None) -> None:
    questions = QUESTION_SETS[qset]
    ids = option_ids(tok)
    sample = pd.read_csv(f"data/sample_{lang}.csv", dtype={"id": str})
    if limit:
        sample = sample.head(limit)
    suffix = "" if qset == "main" else f"_{qset}"
    out = OUT / f"raw_{lang}{suffix}.jsonl"
    todo = sample[~sample["id"].isin(done_ids(out))]
    with out.open("a") as f:
        for row in tqdm(list(todo.itertuples()), desc=f"{lang} {qset}"):
            nouls = {k: p_yes(model, tok, prompt(tok, row.text, q), ids)
                     for k, q in questions.items()}
            record = {"id": row.id, "label": int(row.label), "model": MODEL, "nouls": nouls}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, help="only the first N posts (pilot)")
    args = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    model, tok = load(MODEL)
    for lang in ["en", "tr"]:
        for qset in QUESTION_SETS:
            run(model, tok, lang, qset, args.limit)
