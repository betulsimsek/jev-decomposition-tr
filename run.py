"""Send every sampled post to Jev with all questions in one request.

Monolithic and atomic questions share a request. System One questions are
evaluated independently and cannot see each other's answers, so this is
equivalent to separate requests and half the cost.

Raw responses are appended to results/raw_<lang>.jsonl. Re-running skips
posts that already have a response, so an interrupted run can resume.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

import pandas as pd
from tqdm.asyncio import tqdm
from typesafe_sdk import AsyncTypeSafeClient

from questions import TASKS, state_of

MODEL = "jev-1.13.0"  # pinned, not jev-latest, so results stay reproducible
RESULTS = Path("results")


def load_api_key() -> None:
    if os.environ.get("TYPESAFE_API_KEY"):
        return
    env = Path.home() / ".config/typesafe/.env"
    for line in env.read_text().splitlines():
        if line.startswith("TYPESAFE_API_KEY="):
            os.environ["TYPESAFE_API_KEY"] = line.split("=", 1)[1].strip()


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {json.loads(line)["id"] for line in path.open()}


async def run(task: str, lang: str, qset: str, concurrency: int, limit: int | None) -> None:
    spec = TASKS[task]
    questions = spec["sets"][qset]
    sample = pd.read_csv(spec["data"].format(lang=lang), dtype={"id": str})
    if limit:
        sample = sample.head(limit)
    suffix = "" if qset == "main" else f"_{qset}"
    out = RESULTS / spec["subdir"] / f"raw_{lang}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    todo = sample[~sample["id"].isin(done_ids(out))]
    print(f"{lang}: {len(todo)} to send, {len(sample) - len(todo)} cached")

    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    errors: list[tuple[str, str]] = []

    async with AsyncTypeSafeClient(model=MODEL) as client:
        with out.open("a") as f:

            async def one(row) -> None:
                async with sem:
                    try:
                        resp = await client.system_one(state_of(task, row.text), questions)
                    except Exception as e:  # keep going; a rerun retries it
                        errors.append((row.id, f"{type(e).__name__}: {e}"))
                        return
                record = {
                    "id": row.id,
                    "label": int(row.label),
                    "model": resp.model,
                    "nouls": {k: v.noul for k, v in resp.nouls.items()},
                    "input_tokens": resp.usage.input_tokens,
                }
                async with lock:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    f.flush()

            await tqdm.gather(*(one(r) for r in todo.itertuples()))

    if errors:
        print(f"{len(errors)} failed (rerun to retry). First few:")
        for post_id, msg in errors[:5]:
            print(f"  {post_id}: {msg[:300]}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("lang", choices=["tr", "en"])
    p.add_argument("--task", choices=list(TASKS), default="offense")
    p.add_argument("--set", dest="qset", choices=["main", "bare"], default="main")
    p.add_argument("--concurrency", type=int, default=16)
    p.add_argument("--limit", type=int, help="only the first N posts (pilot)")
    args = p.parse_args()
    load_api_key()
    RESULTS.mkdir(exist_ok=True)
    asyncio.run(run(args.task, args.lang, args.qset, args.concurrency, args.limit))
