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
