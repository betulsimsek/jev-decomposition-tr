"""Download PhishNChips v5.2 and write data/phish_en.csv (id, label, text).

Same file and checksum as jev-phishing-bench's prepare_data.py, so both
benchmarks score the same 2,000 emails (1,000 phishing, 1,000 legitimate).

`text` is the email as a JSON object. Fields are reordered so the sender and
the link come before the body: OpenJev reads only the first 256 state tokens,
and in the dataset's own order the link is the last field. Every backend gets
the same order.
"""

import csv
import hashlib
import json
from pathlib import Path

import httpx
import pandas as pd

URL = "https://huggingface.co/datasets/AreLit/PhishNChips/resolve/main/core_emails.csv"
SHA256 = "cebb407ff8630491a97400e37464b8db8dfc4299164fca51fcb4ac7eec8204ef"  # V5.2 manifest
RAW = Path("data/raw/phishnchips/core_emails.csv")
OUT = Path("data/phish_en.csv")
FIELDS = ["from", "sender", "link_url", "link_display_text", "subject", "body"]


def download() -> None:
    if RAW.exists() and hashlib.sha256(RAW.read_bytes()).hexdigest() == SHA256:
        return
    RAW.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", URL, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        RAW.write_bytes(b"".join(r.iter_bytes()))
    digest = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"checksum mismatch: {digest}, dataset changed upstream")


def main() -> None:
    download()
    csv.field_size_limit(1 << 30)
    with RAW.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        email = json.loads(row["email_content"])
        state = {k: email[k] for k in FIELDS}
        out.append({"id": row["id"], "label": int(row["phish_label"]),
                    "text": json.dumps(state, ensure_ascii=False)})
    df = pd.DataFrame(out).sort_values("id").reset_index(drop=True)
    assert len(df) == 2000 and df["label"].sum() == 1000, (len(df), df["label"].sum())
    df.to_csv(OUT, index=False)
    lengths = df["text"].str.len()
    print(f"{len(df)} emails -> {OUT}; chars median {lengths.median():.0f}, p95 {lengths.quantile(.95):.0f}")


if __name__ == "__main__":
    main()
