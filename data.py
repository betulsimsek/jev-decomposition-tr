"""Build balanced samples of Turkish and English offensive-language posts.

Both corpora use the same OffensEval subtask A annotation scheme:
  TR: OffensEval 2020 Turkish (Çöltekin 2020), official release zip
  EN: OLID / OffensEval 2019 (Zampieri et al. 2019), via cardiffnlp/tweet_eval

Samples are 50/50 OFF/NOT so that base-rate differences between the two
corpora don't leak into calibration comparisons.
"""

import argparse
import csv
from pathlib import Path

import pandas as pd
from datasets import load_dataset

SEED = 42


TR_DIR = Path("data/raw/offenseval2020-turkish/offenseval-tr-testset-v1")


def load_tr() -> pd.DataFrame:
    # The HF repo only ships a loading script (unsupported by datasets>=4), so
    # read the author's official release zip directly. See README for the URL.
    tweets = pd.read_csv(
        TR_DIR / "offenseval-tr-testset-v1.tsv", sep="\t", quoting=csv.QUOTE_NONE,
        dtype=str,
    )
    labels = pd.read_csv(
        TR_DIR / "offenseval-tr-labela-v1.tsv", names=["id", "subtask_a"], dtype=str
    )
    df = tweets.merge(labels, on="id", validate="one_to_one")
    return pd.DataFrame(
        {"id": df["id"], "text": df["tweet"], "label": (df["subtask_a"] == "OFF").astype(int)}
    )


def load_en() -> pd.DataFrame:
    # OLID's test split has only 240 OFF posts, so pool all splits. Nothing is
    # trained on these splits; fitted arms use cross-validation on the sample.
    ds = load_dataset("cardiffnlp/tweet_eval", "offensive")
    parts = []
    for split in ("train", "validation", "test"):
        df = ds[split].to_pandas()
        parts.append(pd.DataFrame(
            {"id": f"en-{split}-" + df.index.astype(str), "text": df["text"], "label": df["label"]}
        ))
    return pd.concat(parts, ignore_index=True)


def balanced(df: pd.DataFrame, per_class: int) -> pd.DataFrame:
    parts = [
        df[df["label"] == y].sample(per_class, random_state=SEED) for y in (0, 1)
    ]
    return pd.concat(parts).sample(frac=1, random_state=SEED).reset_index(drop=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--per-class", type=int, default=500)
    args = p.parse_args()
    Path("data").mkdir(exist_ok=True)
    for lang, loader in [("tr", load_tr), ("en", load_en)]:
        df = loader()
        print(lang, "full:", len(df), "OFF rate:", round(df["label"].mean(), 3))
        balanced(df, args.per_class).to_csv(f"data/sample_{lang}.csv", index=False)
