"""Turn a small local decoder LLM into a Noul scorer with the logprob trick.

Same recipe as Privatemode's "System One from GLM Flash" post: put the state,
the question and numbered options in the prompt, prefill the assistant turn
with "choice_index: ", run one forward pass and read the logits of the option
index tokens, renormalised over the options. No sampling, no parsing.

GLM-5.3-Flash needs ~200 GB of RAM, so this uses Qwen3.5-9B (4-bit, MLX) on
the laptop instead: the question is decoder vs encoder vs Jev, not GLM itself.
Options are always 0 = no, 1 = yes; order bias is not averaged out.

Writes results/qwen/[<task>/]raw_<lang>.jsonl and raw_<lang>_bare.jsonl in
the same format as run.py. Re-running skips items already written.

Phase 4 (--task phish) scores a stratified --sample of emails and reuses the
KV cache of the prompt prefix shared by all of an email's questions (system
message + email), which roughly halves the time. Cached and uncached
probabilities differ by at most ~0.02 in spot checks (4-bit arithmetic order);
every arm of the run uses the same path. The offense run did not use the cache.
"""

import argparse
import copy
import json
from pathlib import Path

import mlx.core as mx
import pandas as pd
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache
from tqdm import tqdm

from questions import TASKS, state_of

MODEL = "mlx-community/Qwen3.5-9B-MLX-4bit"
OUT = Path("results/qwen")
SYSTEM = (
    "You answer a question about a piece of state by choosing one option. "
    "Reply with the index of the correct option only."
)


def prompt(tok, state, question) -> str:
    yes, no = "yes", "no"
    if question.criteria:
        yes = f"yes: {question.criteria['true']}"
        no = f"no: {question.criteria['false']}"
    body = json.dumps(
        {
            "state": state,
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


def p_yes_shared(model, tok, texts: list[str], ids: list[int]) -> list[float]:
    """p_yes for several prompts that share a prefix: prefill it once, fork the cache."""
    toks = [tok.encode(t, add_special_tokens=False) for t in texts]
    n = 0
    while all(len(t) > n + 1 and t[n] == toks[0][n] for t in toks):
        n += 1
    cache = make_prompt_cache(model)
    model(mx.array(toks[0][:n])[None], cache=cache)
    mx.eval([c.state for c in cache])
    out = []
    for t in toks:
        logits = model(mx.array(t[n:])[None], cache=copy.deepcopy(cache))[0, -1]
        out.append(mx.softmax(logits[mx.array(ids)].astype(mx.float32)).tolist()[1])
    return out


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {json.loads(line)["id"] for line in path.open()}


def stratified(df: pd.DataFrame, n: int, seed: int = 0) -> pd.DataFrame:
    """n items, half per label, fixed seed, so every backend can be cut to the same ids."""
    parts = [df[df["label"] == y].sample(n // 2, random_state=seed) for y in (0, 1)]
    return pd.concat(parts).sort_values("id")


def run(model, tok, task: str, lang: str, qset: str, limit: int | None, sample_n: int | None) -> None:
    spec = TASKS[task]
    questions = spec["sets"][qset]
    ids = option_ids(tok)
    sample = pd.read_csv(spec["data"].format(lang=lang), dtype={"id": str})
    if sample_n:
        sample = stratified(sample, sample_n)
    if limit:
        sample = sample.head(limit)
    suffix = "" if qset == "main" else f"_{qset}"
    out = OUT / spec["subdir"] / f"raw_{lang}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    todo = sample[~sample["id"].isin(done_ids(out))]
    shared = task != "offense"  # the offense run predates the prefix cache; keep it reproducible
    with out.open("a") as f:
        for row in tqdm(list(todo.itertuples()), desc=f"{task} {lang} {qset}"):
            state = state_of(task, row.text)
            texts = [prompt(tok, state, q) for q in questions.values()]
            probs = (p_yes_shared(model, tok, texts, ids) if shared and len(texts) > 1
                     else [p_yes(model, tok, t, ids) for t in texts])
            nouls = dict(zip(questions, probs))
            record = {"id": row.id, "label": int(row.label), "model": MODEL, "nouls": nouls}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=list(TASKS), default="offense")
    p.add_argument("--sample", type=int, help="stratified subset of N items (phish: 500)")
    p.add_argument("--limit", type=int, help="only the first N items (pilot)")
    args = p.parse_args()
    model, tok = load(MODEL)
    for lang in TASKS[args.task]["langs"]:
        for qset in TASKS[args.task]["sets"]:
            run(model, tok, args.task, lang, qset, args.limit, args.sample)
