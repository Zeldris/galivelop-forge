"""Ingest filters: personal data (invariant 2) and teacher (invariant 9).

`screen` never edits an example: it keeps it whole or rejects it with the rule and the reason, so what enters a
dataset is exactly what the source exported. The list of real names comes from the caller (a file outside the
repo, `load_names`): a list of real names in the repo would itself be personal data.
"""
import re
from typing import Any, Iterable, List, Optional, Pattern, Sequence, Tuple

from gforge.teachers import teacher_rejection

RULE_EMAIL = "personal-data:email"
RULE_PHONE = "personal-data:phone"
RULE_NAME = "personal-data:name"
RULE_TEACHER = "teacher"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# 9 to 15 digits with optional spaces, dots or dashes between them and an optional +prefix: a phone number;
# shorter runs (years, coins, hit points) are not.
_PHONE = re.compile(r"(?<![\w+])\+?\d(?:[ .-]?\d){8,14}(?!\w)")


class Rejection:
    """Why an example stays out of the dataset."""

    __slots__ = ("id", "rule", "reason")

    def __init__(self, id: str, rule: str, reason: str) -> None:
        self.id = id
        self.rule = rule
        self.reason = reason

    def __repr__(self) -> str:
        return "Rejection(id={!r}, rule={!r}, reason={!r})".format(self.id, self.rule, self.reason)

    def __str__(self) -> str:
        return "{}: {} ({})".format(self.id, self.reason, self.rule)


def load_names(path: str) -> List[str]:
    """Real names to filter, one per line; blank lines and `#` comments are skipped."""
    with open(path, encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.lstrip().startswith("#")]


def _name_patterns(names: Iterable[str]) -> List[Tuple[str, Pattern[str]]]:
    out = []
    for name in names:
        name = " ".join(name.split())
        if name:
            words = r"\s+".join(re.escape(w) for w in name.split(" "))
            out.append((name, re.compile(r"(?<!\w)" + words + r"(?!\w)", re.IGNORECASE)))
    return out


def _personal(text: str, patterns) -> Optional[Tuple[str, str]]:
    if _EMAIL.search(text):
        return RULE_EMAIL, "contains an e-mail address"
    if _PHONE.search(text):
        return RULE_PHONE, "contains a phone number"
    for _name, pattern in patterns:
        if pattern.search(text):
            return RULE_NAME, "contains a real name from the names list"
    return None


def personal_data(text: str, names: Iterable[str] = ()) -> Optional[Tuple[str, str]]:
    """(rule, reason) for the first personal datum in `text`, or None. The reason never repeats the datum."""
    return _personal(text, _name_patterns(names))


def _texts(example) -> Iterable[Tuple[str, str]]:
    for field in ("messages", "prompt", "chosen", "rejected"):
        for index, message in enumerate(getattr(example, field, None) or ()):
            yield "{}[{}]".format(field, index), message["content"]


def check(example, names: Sequence[str] = ()) -> Optional[Rejection]:
    """The rejection of one example (teacher first, then personal data), or None if it passes."""
    return _check(example, _name_patterns(names))


def _check(example, patterns) -> Optional[Rejection]:
    reason = teacher_rejection(getattr(example, "teacher", None))
    if reason:
        return Rejection(example.id, RULE_TEACHER, reason)
    for where, text in _texts(example):
        found = _personal(text, patterns)
        if found:
            return Rejection(example.id, found[0], "{} {}".format(where, found[1]))
    return None


def screen(examples: Iterable, names: Sequence[str] = ()) -> Tuple[list, List[Rejection]]:
    """Split examples into (kept, rejections), keeping the input order."""
    patterns = _name_patterns(names)
    kept, rejections = [], []
    for example in examples:
        rejection = _check(example, patterns)
        if rejection is None:
            kept.append(example)
        else:
            rejections.append(rejection)
    return kept, rejections
