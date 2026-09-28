# Most of Jev's 62.6%→95% phishing jump was the definition; other models differ

**TL;DR.** The most-shared result about TypeSafe's Jev is phishing
detection going from 62.6% asked once to 95% when the question is split
into five atomic signals with fitted weights
([jev-phishing-bench](https://github.com/anisselbd/jev-phishing-bench)).
On the same 2,000 PhishNChips emails both numbers replicate (61.8%, 95.2%),
and the arm the original didn't test, **one question with the five signals
written in as a definition, gets 88.2% with no labels**. For Jev, about 26
of the ~33 points are the definition.

That split is Jev's. Two open decision models reach a similar total by
different routes (accuracy points, phishing):

| | add definition | then split + fit | total |
|---|---|---|---|
| Jev | **+28.3*** | +5.4* | +35.3 |
| Laya (encoder) | +12.3* | **+16.3*** | +28.7 |
| OpenJev (encoder) | −1.4 | **+32.7*** | +32.4 |

The same pattern on 2,000 English and Turkish tweets (offensive language),
with Qwen3.5-9B as a fourth model:

| accuracy (EN) | Jev | Qwen3.5-9B (decoder) | Laya (encoder) | OpenJev (encoder) |
|---|---|---|---|---|
| add the full definition | +4.5* | +3.4 | **−11.0*** | **−11.4*** |
| split + noisy-OR, ECE | worse* | worse* | **better*** | worse* |
| split + fitted weights | +2.4* | +3.9* | +2.6* | +4.1* |

- **Split + fitted weights never hurt significantly**, on any model, task
  or language. It is the only prompt-shape rule that transferred.
- **The definition's effect depends on model and task.** Laya: −11 on
  tweets, +12 on emails. OpenJev: breaks on a long definition (a
  one-sentence version works on tweets) and can't do phishing from any
  single question.
- **Noisy-OR's effect follows the model's starting bias.** It pushes
  probabilities up: eager models get worse, timid Laya on tweets gets
  better. On phishing every model turns eager under it, and every model
  loses calibration.
- **Splitting helps less in Turkish** on every model that reads Turkish.

`*` = 95% paired-bootstrap CI excludes zero. Details: Phase 1 (Jev) below,
[Phase 2](#phase-2-is-it-a-jev-quirk) (Laya, Qwen),
[Phase 3](#phase-3-is-layas-timidity-an-encoder-thing) (OpenJev),
[Phase 4](#phase-4-the-62695-claim-on-its-own-data) (phishing). Full
tables: [`results/compare.md`](results/compare.md) (tweets),
[`results/phish/compare.md`](results/phish/compare.md) (emails).

## Phase 1: most of Jev's decomposition gain was the definition

An independent test of TypeSafe's Jev (`jev-1.13.0`) on one open question:
**does splitting a judgment into atomic questions help, and does that hold
outside English?** Tested on offensive-language detection in English and
Turkish, 1,000 posts each, 4,000 requests, **$0.07** total.

![Reliability diagram](results/reliability.png)

## Why this question

Two published results point in opposite directions:

- Asking "is this phishing?" once scored **62.6%**; splitting it into five
  narrow questions with fitted weights reached **95.0%**
  ([report](https://www.beri.net/article/typesafe-jev-typed-decision-model-calibration-decomposition-shadow-eval)).
- On 60 multilingual phrases, splitting one decision into three questions
  **dropped calibration from 1.00 to 0.55 / 0.42**
  ([awesome-jev-robustness](https://github.com/Yifan-Lan/awesome-jev-robustness)).

No one had separated what the split itself contributes from two confounds:
(1) the one-shot baseline carried **no definition**, and (2) fitting weights
on labels **also recalibrates** the output. And no audit covered Turkish, an
agglutinative language where negation, tense, and mood live in suffixes.

## Setup

| | |
|---|---|
| Task | OffensEval subtask A: offensive (profanity or targeted offense, veiled or direct) vs not |
| English | OLID / OffensEval 2019 ([Zampieri et al. 2019](https://aclanthology.org/N19-1144/)), via `cardiffnlp/tweet_eval` |
| Turkish | OffensEval 2020 Turkish ([Çöltekin 2020](https://aclanthology.org/2020.lrec-1.758/)) |
| Sample | 1,000 posts per language, 500 OFF / 500 NOT, seed 42 |
| Model | `jev-1.13.0`, pinned |
| Questions | Identical English instructions for both languages; only the post changes language |

Both corpora use the same annotation scheme, so the task definition is
identical across languages. The two corpora are **not parallel**, so absolute
accuracy is not comparable between languages; the comparisons that matter
are **within-language effects** and how they differ (TR − EN).

### Arms

| Arm | What it is | Labels used? |
|---|---|---|
| `B-raw` | Bare question: "Is this social media post offensive?" | no |
| `B-fit` | `B-raw`, Platt-scaled | yes |
| `M-raw` | One question carrying the full OffensEval definition | no |
| `M-fit` | `M-raw`, Platt-scaled | yes |
| `D-noisyor` | 5 atomic Nouls (profanity, insult, threat, identity attack, veiled offense), combined with noisy-OR | no |
| `D-fit` | Logistic regression over the 5 atomic Nouls | yes |
| `MD-fit` | Logistic regression over definition + atomic Nouls | yes |

Fitted arms use 5-fold out-of-fold predictions. Intervals are 95% bootstrap
(1,000 resamples); effects use paired bootstrap on the same posts. The bare
question was sent in its own request; all other questions share one request
(System One questions are evaluated independently).

## Results

Accuracy at threshold 0.5 (AUC in parentheses):

| Arm | English | Turkish |
|---|---|---|
| `B-raw` bare, asked once | 0.693 (0.775) | 0.813 (0.904) |
| `M-raw` with definition, asked once | 0.738 (0.819) | 0.828 (0.921) |
| `D-noisyor` split, no fitting | **0.615** (0.749) | **0.726** (0.898) |
| `D-fit` split + fitted weights | 0.759 (0.827) | 0.836 (0.914) |
| `MD-fit` definition + split, fitted | 0.761 (0.837) | 0.847 (0.922) |

Expected calibration error (lower is better):

| Arm | English | Turkish |
|---|---|---|
| `M-raw` | 0.087 | 0.061 |
| `M-fit` | 0.035 | 0.026 |
| `D-noisyor` | **0.306** | **0.233** |
| `D-fit` | 0.046 | 0.025 |

Effects, accuracy points [95% CI]:

| Effect | English | Turkish | TR − EN |
|---|---|---|---|
| "Asked once" → "split + fitted" (`D-fit` − `B-fit`) | **+5.9** [+3.3, +8.4] | +1.9 [−0.2, +4.0] | **−4.0** [−7.3, −0.6] |
| of which: adding the definition (`M-raw` − `B-raw`) | **+4.5** [+2.5, +6.4] | +1.5 [−0.3, +3.2] | **−3.0** [−5.7, −0.3] |
| of which: splitting, both fitted (`D-fit` − `M-fit`) | +2.4 [+0.1, +4.7] | −0.7 [−2.4, +1.0] | −3.1 [−5.7, −0.1] |
| Splitting without fitting (`D-noisyor` − `M-raw`) | **−12.3** [−15.5, −9.1] | **−10.2** [−13.7, −7.0] | +2.1 [−2.3, +6.4] |

Full tables with macro-F1, Brier, and CIs for every cell: [`results/summary.md`](results/summary.md).

## What this says

1. **Both published results reproduce, and they don't conflict.** Splitting
   with fitted weights beats a bare one-shot question (+5.9 in English).
   Splitting *without* fitting wrecks calibration (ECE 0.09 → 0.31), because
   noisy-OR treats five correlated judgments as independent evidence and
   becomes badly overconfident. The two results measured different things.

2. **Most of the English "decomposition" gain is the definition.** Of the
   +5.9 points, +4.5 appear by writing the annotation definition into a
   single question. Splitting on top of that adds +2.4, barely clear of zero.
   Before splitting a question, try defining it.

3. **In Turkish, decomposition added nothing detectable.** Neither the
   definition nor the split moved accuracy significantly, and both effects
   are smaller than in English (TR − EN interaction −4.0 points, CI excludes
   zero). Jev's single bare question was already well calibrated on Turkish
   (ECE 0.064).

4. **The morphology hypothesis is not supported.** Splitting did not *hurt*
   Turkish; it just didn't help. That fits a ceiling effect or a
   corpus difference at least as well as anything about suffixes.

## Phase 2: is it a Jev quirk?

Same posts, questions, arms and analysis code, with two open backends:

| Backend | Architecture | How | Script |
|---|---|---|---|
| Jev `jev-1.13.0` | closed, hosted | TypeSafe API | `run.py` |
| Laya `multilingual` | encoder (ModernBERT), open | local, `pip install laya` | `run_laya.py` |
| Qwen3.5-9B 4-bit | decoder LLM, open | local MLX, logprob trick from Privatemode's "System One from GLM Flash" | `run_decoder.py` |

GLM-5.3-Flash itself needs ~200 GB of RAM, so a 9B decoder stands in for it.

Effects (paired bootstrap, `*` = 95% CI excludes zero; full table in
`results/compare.md`):

| effect | Jev EN | Jev TR | Laya EN | Laya TR | Qwen EN | Qwen TR |
|---|---|---|---|---|---|---|
| add definition (M-raw − B-raw), accuracy | +0.045* | +0.015 | **−0.110*** | **−0.077*** | +0.034 | −0.015 |
| naive split (D-noisyor − M-raw), accuracy | −0.123* | −0.102* | **+0.148*** | **+0.079*** | −0.133* | −0.175* |
| naive split, ECE | +0.219* | +0.172* | **−0.201*** | **−0.115*** | +0.232* | +0.276* |
| split + fit (D-fit − M-fit), AUC | +0.009 | −0.007 | +0.039* | +0.023* | +0.028* | +0.010* |

Mean P(offensive) on offensive / non-offensive posts, English:

| | bare | with definition | noisy-OR |
|---|---|---|---|
| Jev | 0.65 / 0.37 | 0.71 / 0.33 | 0.91 / 0.70 |
| Laya | 0.55 / 0.19 | **0.32 / 0.10** | 0.71 / 0.29 |
| Qwen | **0.78 / 0.49** | 0.60 / 0.29 | 0.93 / 0.77 |

- **The odd one out is Laya, not Jev.** Qwen follows Jev's rules; Laya
  flips two of them. One model per architecture, so this is not a claim
  about encoders in general.
- **What decides it is the model's starting bias.** The definition and
  noisy-OR both move probabilities: the definition pulls them down, noisy-OR
  pushes them up. Eager Qwen (0.49 on non-offensive posts) is fixed by the
  definition and wrecked by noisy-OR. Timid Laya (0.32 on offensive posts
  once it sees the definition) is the reverse. Laya's ranking barely moves;
  the loss is a threshold shift.
- **Splitting helps less in Turkish on all three backends.** Split + fit AUC
  gain: Jev +0.9 → −0.7, Laya +3.9 → +2.3, Qwen +2.8 → +1.0 points. Only
  Jev drops to zero. A ceiling effect fits Jev but not Laya (Turkish AUC
  0.73); language and corpus can't be separated here.
- **Split + fit (D-fit) never hurt significantly** on any backend or
  language, and improved accuracy significantly in 4 of 6.

Rule of thumb: before porting prompt-shape rules to a new decision model,
check its mean prediction on a few hundred labelled examples. If it is eager,
noisy-OR hurts; if it is timid, it helps. Whether a definition helps has to
be measured (Phase 3). With labels, split and fit.

```bash
uv run run_laya.py                 # ~10 min on an M3 -> results/laya/
uv run run_decoder.py              # hours; resumable -> results/qwen/
uv run analyze.py --backend laya   # per-backend summary.md
uv run compare.py                  # side by side -> results/compare.md
```

## Phase 3: is Laya's timidity an encoder thing?

Laya is one encoder, so Phase 2 couldn't say whether its behaviour belongs to
encoders or to Laya. Phase 3 adds a second, independently trained encoder
with the same instructions + yes/no interface:
[OpenJev](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large)
(DeBERTa-v3-large, trained on banking77, SST-5 and BoolQ; English-only, so
only its English numbers are interpreted). `run_openjev.py` sends each
question on its own, because the model otherwise packs all questions into
one sequence, and appends the one question's criteria to its instructions.

| effect (EN) | Laya | OpenJev |
|---|---|---|
| add definition, accuracy | −0.110* | −0.114* |
| add definition, ECE | +0.142* | +0.217* |
| split + noisy-OR, ECE | −0.201* | +0.072* |
| split + fit (D-fit − M-fit), accuracy | +0.026* | +0.041* |
| split + fit, AUC | +0.039* | +0.055* |

Mean P(offensive) on offensive / non-offensive posts, English:

| | bare | full definition | one-sentence definition |
|---|---|---|---|
| Laya | 0.55 / 0.19 | **0.32 / 0.10** | 0.38 / 0.10 |
| OpenJev | 0.70 / 0.47 | **0.88 / 0.77** | 0.55 / 0.36 |

- **Timidity is Laya's, not the encoders'.** With the full definition
  OpenJev goes the other way and calls almost everything offensive ("The
  meeting is at 3pm in room 204." scores 0.94). Noisy-OR then hurts it like
  it hurts the other eager models.
- **Both encoders are hurt by the definition, for different reasons.**
  `probe_short_def.py` asks the same definition in one sentence. OpenJev
  recovers (ECE 0.078, better than bare), so its failure is the length of a
  four-sentence instruction it never saw in training. Laya stays timid
  (accuracy −6.8 EN / −7.8 TR vs bare, AUC unchanged), so its failure is how
  it reads the definition's content. Exploratory; see
  `results/probe_short_def.md`.
- **Split + fit is still safe**, and helps OpenJev most of all.

```bash
uv run run_openjev.py              # ~20 min on an M3 -> results/openjev/
uv run probe_short_def.py          # -> results/probe_short_def.md
```

## Phase 4: the 62.6%→95% claim on its own data

The claim that started this came from
[jev-phishing-bench](https://github.com/anisselbd/jev-phishing-bench):
PhishNChips v5.2, 2,000 emails (1,000 phishing), Jev and Claude Haiku only,
single question vs five atomic signals + logistic regression. Phase 4 runs
the same file (same SHA-256) through the same arms as Phases 1-3.

- **State:** the email as a JSON object. Sender and link fields come before
  the body, because OpenJev reads only the first 256 state tokens (11% of
  emails are longer; the header fields average 78 tokens).
- **Questions** (`questions.py`, `PHISH_SETS`): a bare question; our
  monolithic question with the five signals written in as a definition;
  the original five atomic signal questions, verbatim; and the original
  single question with its criteria, verbatim, kept only to compare with
  the published 62.6%.
- **Analysis:** 5-fold out-of-fold fitting and paired bootstrap, as before.
  The original used a 50/50 select/evaluate split; the headline numbers
  still match.

| accuracy | Jev | Laya | OpenJev |
|---|---|---|---|
| original single question | 0.618 (published 0.626) | 0.789 | 0.500 |
| bare (B-raw) | 0.599 | 0.610 | 0.500 |
| with definition (M-raw) | **0.882** | 0.733 | 0.486 |
| split + noisy-OR (D-noisyor) | 0.794 | 0.589 | 0.500 |
| split + fitted weights (D-fit) | **0.952** (published 0.951) | **0.897** | **0.824** |

- **Jev:** the definition alone is worth +28.3 points with no labels;
  splitting and fitting add +5.4 on top and give the best calibration
  (ECE 0.016).
- **Laya:** the definition helps here (+12.3) though it hurt on tweets
  (−11.0); splitting and fitting add +16.3. Its best single question is
  the original criteria wording (78.9%).
- **OpenJev:** no single question separates the classes (AUC 0.37–0.46)
  while the atomic questions work (split + fit AUC 0.894). Its training
  data (banking77, SST-5, BoolQ) has field-level yes/no questions but no
  holistic "is this phishing?" judgment; that is a guess, not tested.
- **Noisy-OR** makes every model eager on legitimate mail (mean
  P(phishing) 0.55 / 0.72 / 0.94), because the atomic signals fire on
  legitimate emails too (e.g. company files shared through Google Drive).

Jev cost $0.11 for Phase 4. Qwen is not included: emails are 3-4× longer
than tweets and the run would take over a day on a laptop.

```bash
uv run data_phish.py                            # -> data/phish_en.csv (checksum-verified)
uv run run.py en --task phish                   # Jev, then: --set bare
uv run run_laya.py --task phish
uv run run_openjev.py --task phish
uv run analyze.py --backend jev --task phish    # -> results/phish/summary.md
uv run compare.py --task phish                  # -> results/phish/compare.md
```

## Limitations

- One model per backend; Jev's architecture is not public, so
  "decoder vs encoder" can't be read off these results.
- Two tasks. PhishNChips email bodies are synthetic (LLM-written; the
  links are real). Only one definition text was tried per task.
- Both tasks have a crisp definition. Tasks without one may benefit more
  from splitting.
- The tweet corpora are not parallel. Turkish scoring higher overall almost
  certainly reflects the datasets (OLID is known to be noisy), not the
  language. Only within-language effects are interpreted.
- All data is public and may be in training sets; contamination would
  affect every arm of a model alike, not the differences between arms.
- Instructions are English for both languages. Turkish instructions are an
  untested follow-up.
- One atomic question set, one combination rule per arm, one model version.
  Jev returns probabilities rounded to two decimals.
- Classes are 50/50 in both tasks; calibration at natural base rates was
  not measured.

## Reproduce

```bash
uv sync
curl -sL -o data/raw/offenseval2020-turkish.zip --create-dirs \
  https://coltekin.github.io/offensive-turkish/offenseval2020-turkish.zip
unzip -oq data/raw/offenseval2020-turkish.zip -d data/raw
uv run data.py                     # balanced samples -> data/
export TYPESAFE_API_KEY=...
uv run run.py tr && uv run run.py en                 # main question set
uv run run.py tr --set bare && uv run run.py en --set bare
uv run analyze.py                  # -> results/summary.md, reliability.png
```

### Local UI

```bash
uv run streamlit run app.py        # http://localhost:8501
```

Three tabs: **Dene** (type a sentence, see every arm and the atomic
breakdown live; 2 requests per try), **Sonuçlar** (metrics with CIs,
interactive reliability diagram, effects table), and **Örnekler** (posts
where arms disagree, e.g. "definition helped" or "noisy-OR false alarm").
The UI imports `analyze.py`, so its numbers match `results/summary.md`.

Or in Docker (the key is read at runtime, never baked into the image):

```bash
docker build -t jev-decomposition-tr .
docker run -d -p 127.0.0.1:8501:8501 --env-file ~/.config/typesafe/.env jev-decomposition-tr
```

`results/raw_*.jsonl` holds every raw Noul probability (post ids and labels,
no post text), so `analyze.py` runs without an API key.

Data licenses: OffensEval-TR is CC-BY 2.0; OLID via TweetEval. Post text is
not redistributed here; `data.py` rebuilds the samples deterministically.
