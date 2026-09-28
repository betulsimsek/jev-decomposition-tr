"""Question set for the decomposition experiment.

Both languages get the exact same English instructions; only the state
(the tweet) changes language. That keeps text language as the only variable.

The monolithic question carries the full OffensEval annotation definition.
The atomic questions split that definition into the conditions it is made of.
"""

from typesafe_sdk import Noul, NoulCriteria

# OffensEval subtask A definition (Zampieri et al. 2019; Çöltekin 2020):
# OFF = any non-acceptable language (profanity) or a targeted offense,
# veiled or direct. NOT = neither.
MONOLITHIC = {
    "offensive": Noul(
        instructions=(
            "Is this social media post offensive? A post is offensive if it "
            "contains any form of non-acceptable language (profanity) or a "
            "targeted offense, which can be veiled or direct. This includes "
            "insults, threats, and posts containing profane language or swear "
            "words."
        ),
    ),
}

ATOMIC = {
    "profanity": Noul(
        instructions=(
            "Does the post contain any profanity, swear words, or vulgar "
            "language, including censored, abbreviated, or misspelled forms?"
        ),
    ),
    "insult": Noul(
        instructions=(
            "Does the post insult, demean, or ridicule a specific person or "
            "group?"
        ),
    ),
    "threat": Noul(
        instructions="Does the post threaten or wish harm on anyone?",
    ),
    "identity_attack": Noul(
        instructions=(
            "Does the post attack people for who they are, such as their "
            "ethnicity, religion, gender, sexual orientation, nationality, or "
            "political affiliation?"
        ),
    ),
    "veiled": Noul(
        instructions=(
            "Does the post contain a veiled or indirect offense aimed at "
            "someone, such as sarcastic mockery or a derogatory innuendo?"
        ),
        criteria=NoulCriteria(
            true="The offense is implied rather than stated outright",
            false="No implied offense; either none at all or only explicit",
        ),
    ),
}

ALL = {**MONOLITHIC, **ATOMIC}
ATOMIC_KEYS = list(ATOMIC)

# Follow-up arm: the same judgment asked with no definition at all, like the
# "is this phishing?" baseline in the 62.6% -> 95% report. Sent in its own
# request so it cannot share a request with the definition-bearing questions.
BARE = {
    "offensive_bare": Noul(instructions="Is this social media post offensive?"),
}

QUESTION_SETS = {"main": ALL, "bare": BARE}


# ---------------------------------------------------------------------------
# Phase 4: PhishNChips, the dataset behind the "62.6% asked once, 95% split
# five ways" claim (github.com/anisselbd/jev-phishing-bench). The five atomic
# questions and the "original" single question are copied verbatim from that
# benchmark's run_jev.py. The monolithic question is ours: the same five
# signals written into one definition, mirroring MONOLITHIC above. The state is
# the email as a JSON object, so questions can name its fields.

PHISH_MONOLITHIC = {
    "phishing": Noul(
        instructions=(
            "Is this email a phishing attempt? An email is phishing if it tries "
            "to get the user to click a malicious link. Signs include: the "
            "domain of the sender address in `from` differs from the "
            "organization or domain the link in `link_url` points to; the link "
            "points to a URL shortener or a free hosting or file-sharing "
            "platform rather than the organization's own website; the email "
            "asks the user to sign in, verify an account, or open a document "
            "through the link; it pressures the user to act quickly or "
            "threatens a consequence; or the sender uses a generic webmail "
            "address while presenting themselves as an organization."
        ),
    ),
}

PHISH_ATOMIC = {
    "sig_domain_mismatch": Noul(
        instructions=(
            "The domain of the sender address in `from` is different from the "
            "organization or domain that the link in `link_url` points to."
        ),
    ),
    "sig_free_hosting": Noul(
        instructions=(
            "The link in `link_url` points to a URL shortener or to a free "
            "hosting or file-sharing platform (for example bit.ly, an IPFS "
            "gateway, Firebase, GitHub Pages, Google Docs) rather than to the "
            "organization's own website."
        ),
    ),
    "sig_lure": Noul(
        instructions=(
            "The email asks the user to sign in, verify an account, or open a "
            "document or file through the link."
        ),
    ),
    "sig_urgency": Noul(
        instructions=(
            "The email pressures the user to act quickly, mentions a deadline, "
            "or threatens a consequence."
        ),
    ),
    "sig_generic_sender": Noul(
        instructions=(
            "The sender uses a generic webmail address (such as gmail, outlook, "
            "yahoo, hotmail) in `from` while presenting themselves as a "
            "company, team, department or organization."
        ),
    ),
}

# jev-phishing-bench's own single question (their "mirror Noul"), kept for
# reference against their published 62.6%; it is not one of the analysis arms.
PHISH_ORIGINAL = {
    "phishing_original": Noul(
        instructions=(
            "This email is a phishing attempt and the user should not click "
            "the link in `link_url`."
        ),
        criteria=NoulCriteria(
            true="The email or its link is a phishing attempt or otherwise malicious.",
            false="The email is a normal, legitimate message and the link is safe to click.",
        ),
    ),
}

PHISH_BARE = {
    "phishing_bare": Noul(instructions="Is this email a phishing attempt?"),
}

PHISH_SETS = {
    "main": {**PHISH_MONOLITHIC, **PHISH_ATOMIC, **PHISH_ORIGINAL},
    "bare": PHISH_BARE,
}

# One entry per task: which questions, languages and data file, and which
# question keys play the bare / monolithic / atomic roles in analyze.py.
TASKS = {
    "offense": {
        "sets": QUESTION_SETS, "langs": ["en", "tr"], "data": "data/sample_{lang}.csv",
        "bare": "offensive_bare", "mono": "offensive", "atomic": ATOMIC_KEYS, "subdir": "",
    },
    "phish": {
        "sets": PHISH_SETS, "langs": ["en"], "data": "data/phish_{lang}.csv",
        "bare": "phishing_bare", "mono": "phishing", "atomic": list(PHISH_ATOMIC), "subdir": "phish",
    },
}


def state_of(task: str, text: str):
    """What the model sees: the post under a key for offense, the email object for phish."""
    import json

    return {"post": text} if task == "offense" else json.loads(text)
