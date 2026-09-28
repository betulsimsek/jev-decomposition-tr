"""Exploratory: do the two encoders fail on the definition, or on its length?

Both encoders lose accuracy when the bare question gets the full four-sentence
OffensEval definition, but in opposite directions (Laya turns timid, OpenJev
calls almost everything offensive). This asks the same definition in one
sentence and compares it with the bare and full-definition arms already on disk.

Not part of analyze.py's arms; writes results/probe_short_def.md.
"""

import sys

import numpy as np
import pandas as pd
from huggingface_hub import snapshot_download
from laya import Router

from analyze import METRICS, RESULTS, load, paired_diff

SHORT = ("Is this post offensive, i.e. does it contain profanity or a targeted "
         "insult or threat?")
LANGS = {"laya": ["en", "tr"], "openjev": ["en"]}  # OpenJev is English-only


def score_laya(texts: list[str]) -> np.ndarray:
    router = Router()
    q = {"s": {"type": "noul", "instructions": SHORT}}
    out = router.predict_batch([{"state": {"post": t}, "questions": q, "model": "multilingual"}
                                for t in texts], batch_size=32)
    return np.array([o["answers"]["s"]["noul"] for o in out])


def score_openjev(texts: list[str]) -> np.ndarray:
    path = snapshot_download("com-kotobalabs/open-jev-deberta-v3-large")
    sys.path.insert(0, path)
    from typed_decisions.open_jev import OpenJev
    m = OpenJev.from_pretrained(path)
    return np.array([m.decide(t, [{"type": "noul", "instructions": SHORT}])[0]["noul"] for t in texts])


def main() -> None:
    lines = ["# Probe: short one-sentence definition (exploratory)\n",
             f"Short definition: *{SHORT}*\n",
             "| backend | lang | arm | accuracy | AUC | ECE | mean P on OFF / NOT |",
             "|---|---|---|---|---|---|---|"]
    effects = ["\n## Short definition vs bare (paired bootstrap, `*` = 95% CI excludes zero)\n",
               "| backend | lang | accuracy | AUC | ECE |", "|---|---|---|---|---|"]
    for backend, langs in LANGS.items():
        for lang in langs:
            df = load(lang, RESULTS / backend)
            texts = pd.read_csv(f"data/sample_{lang}.csv", dtype={"id": str}).set_index("id").loc[df["id"], "text"]
            y = df["label"].to_numpy()
            short = (score_laya if backend == "laya" else score_openjev)(list(texts))
            arms = {"bare": df["offensive_bare"].to_numpy(), "full definition": df["offensive"].to_numpy(),
                    "short definition": short}
            for arm, p in arms.items():
                lines.append(f"| {backend} | {lang.upper()} | {arm} | {METRICS['accuracy'](y, p):.3f} | "
                             f"{METRICS['auc'](y, p):.3f} | {METRICS['ece'](y, p):.3f} | "
                             f"{p[y == 1].mean():.2f} / {p[y == 0].mean():.2f} |")
            cells = []
            for name in ["accuracy", "auc", "ece"]:
                d, lo, hi = paired_diff(y, arms["bare"], short, METRICS[name])
                cells.append(f"{d:+.3f}{'' if lo <= 0 <= hi else '*'}")
            effects.append(f"| {backend} | {lang.upper()} | " + " | ".join(cells) + " |")
    text = "\n".join(lines + effects) + "\n"
    (RESULTS / "probe_short_def.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
