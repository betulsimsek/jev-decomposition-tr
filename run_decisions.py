"""Send every sampled item to OpenAI's Decisions API with the same questions as Jev.

Each Noul becomes a `predicate` question (Decisions' probability-of-true type).
A Noul's criteria, which Decisions has no field for, are appended to the
instructions as "True if ... / False if ...". The state goes in as an
`input_json` part, so the model sees the same object Jev sees.

Like run.py, monolithic and atomic questions share a request, and the bare
question gets its own. Writes results/decisions/<subdir>/raw_<lang>[_bare].jsonl
in run.py's format, so analyze.py and compare.py read it unchanged. Re-running
skips items that already have a response. A refused question is stored as
null and counted.

Docs: https://developers.openai.com/api/docs/guides/decisions
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

import httpx
import pandas as pd
from tqdm.asyncio import tqdm

from questions import TASKS, state_of

MODEL = "gpt-6-luna"  # the only model Decisions supports
URL = "https://api.openai.com/v1/decisions"
OUT = Path("results/decisions")
PRICE_PER_M_INPUT = 0.10  # USD, uncached; output is free


def load_api_key() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    env = Path.home() / ".config/openai/.env"
    for line in env.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"OPENAI_API_KEY not set and not in {env}")


def to_decisions(questions: dict) -> list[dict]:
    out = []
    for name, q in questions.items():
        text = q.instructions
        if q.criteria:
            c = dict(q.criteria)
            text += f"\nTrue if: {c['true']}\nFalse if: {c['false']}"
        out.append({"type": "predicate", "name": name, "instructions": text})
    return out


def payload(task: str, text: str, questions: list[dict]) -> dict:
    return {
        "model": MODEL,
        "input": [{"role": "user", "content": [{"type": "input_json", "data": state_of(task, text)}]}],
        "questions": questions,
    }


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {json.loads(line)["id"] for line in path.open()}


def plan(task: str, lang: str, qset: str, limit: int | None):
    spec = TASKS[task]
    sample = pd.read_csv(spec["data"].format(lang=lang), dtype={"id": str})
    if limit:
        sample = sample.head(limit)
    suffix = "" if qset == "main" else f"_{qset}"
    out = OUT / spec["subdir"] / f"raw_{lang}{suffix}.jsonl"
    todo = sample[~sample["id"].isin(done_ids(out))]
    return to_decisions(spec["sets"][qset]), todo, out


def estimate(task: str, lang: str, qset: str, limit: int | None) -> float:
    """Rough input-token count (4 chars per token) and cost for what is left to send."""
    questions, todo, _ = plan(task, lang, qset, limit)
    chars = sum(len(json.dumps(payload(task, t, questions), ensure_ascii=False)) for t in todo.text)
    tokens = chars / 4
    cost = tokens / 1e6 * PRICE_PER_M_INPUT
    print(f"{task} {lang} {qset}: {len(todo)} requests, ~{tokens / 1e6:.2f}M input tokens, ~${cost:.2f}")
    return cost


async def run(key: str, task: str, lang: str, qset: str, concurrency: int, limit: int | None) -> None:
    questions, todo, out = plan(task, lang, qset, limit)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"{task} {lang} {qset}: {len(todo)} to send")

    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    errors: list[tuple[str, str]] = []
    refusals = 0

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {key}"}, timeout=120) as client:
        with out.open("a") as f:

            async def one(row) -> None:
                nonlocal refusals
                r = None
                async with sem:
                    for attempt in range(5):
                        try:
                            r = await client.post(URL, json=payload(task, row.text, questions))
                        except httpx.TransportError as e:  # dropped connection; retry
                            r = None
                            last = f"{type(e).__name__}: {e}"
                        else:
                            if r.status_code not in (429, 500, 502, 503):
                                break
                            last = f"{r.status_code}: {r.text[:300]}"
                        await asyncio.sleep(2 ** attempt * 2)
                if r is None:
                    errors.append((row.id, last))
                    return
                if r.status_code != 200:
                    errors.append((row.id, f"{r.status_code}: {r.text[:300]}"))
                    return
                body = r.json()
                nouls = {}
                for a in body["answers"]:
                    if a["type"] == "refusal":
                        refusals += 1
                        nouls[a["name"]] = None
                    else:
                        nouls[a["name"]] = a["probability"]
                record = {
                    "id": row.id,
                    "label": int(row.label),
                    "model": body.get("model", MODEL),
                    "nouls": nouls,
                    "input_tokens": body.get("usage", {}).get("input_tokens"),
                }
                async with lock:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    f.flush()

            await tqdm.gather(*(one(r) for r in todo.itertuples()))

    if refusals:
        print(f"{refusals} refused questions stored as null")
    if errors:
        print(f"{len(errors)} failed (rerun to retry). First few:")
        for item_id, msg in errors[:5]:
            print(f"  {item_id}: {msg}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("lang", choices=["tr", "en"])
    p.add_argument("--task", choices=list(TASKS), default="offense")
    p.add_argument("--set", dest="qset", choices=["main", "bare"], default="main")
    p.add_argument("--concurrency", type=int, default=16)
    p.add_argument("--limit", type=int, help="only the first N items (pilot)")
    p.add_argument("--estimate", action="store_true", help="print the request count and cost, send nothing")
    p.add_argument("--show", action="store_true", help="print the first request body, send nothing")
    args = p.parse_args()
    if args.show:
        qs, todo, _ = plan(args.task, args.lang, args.qset, 1)
        print(json.dumps(payload(args.task, todo.text.iloc[0], qs), ensure_ascii=False, indent=2))
    elif args.estimate:
        estimate(args.task, args.lang, args.qset, args.limit)
    else:
        asyncio.run(run(load_api_key(), args.task, args.lang, args.qset, args.concurrency, args.limit))
