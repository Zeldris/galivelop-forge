"""Ingest filters: personal data (invariant 2) and teacher (invariant 9).

`screen` never edits an example: it keeps it whole or rejects it with the rule and the reason, so what enters a
dataset is exactly what the source exported. The list of real names comes from the caller (a file outside the
repo, `load_names`): a list of real names in the repo would itself be personal data.
"""
import json
import re
import unicodedata
from typing import Any, Iterable, List, Optional, Pattern, Sequence, Tuple

from gforge.teachers import teacher_rejection

RULE_EMAIL = "personal-data:email"
RULE_PHONE = "personal-data:phone"
RULE_NAME = "personal-data:name"
RULE_TEACHER = "teacher"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# A run of digit groups (optionally in parentheses, optional +prefix) joined by any run of separators (Unicode
# spaces, dots, dashes, slashes); it is a phone number when it has 9 to 15 digits. Commas and words end the run,
# so "12-15, vida 80/100" never adds up.
_GROUP = r"(?:\(\s*)?\d+(?:\s*\))?"
_SEP = r"[\s.\-\u2013\u2014/]+"
_PHONE = re.compile(r"(?<![\w+])\+?" + _GROUP + r"(?:" + _SEP + _GROUP + r")*(?!\w)")
# An ISO date, optionally with a day range ("2026-07-21/22"), standing on its own: it is dropped before looking for
# phones, since its 10 digits would add up. One glued to other digit groups ("91 2026-07-21") is kept, so a phone
# that happens to contain a date shape is still caught.
_ISO_DATE = re.compile(r"(?<![\w+.\-\u2013\u2014/])(?<!\d\s)(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])"
                       r"(?:/(?:0[1-9]|[12]\d|3[01]))?(?!\w|" + _SEP + r"\(?\d)")


def _has_phone(text: str) -> bool:
    text = _ISO_DATE.sub(" ", text)
    return any(9 <= sum(c.isdigit() for c in m.group()) <= 15 for m in _PHONE.finditer(text))


def _fold(text: str) -> str:
    """NFKD, no combining marks, casefolded: accents, case and Unicode form do not hide a name."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


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
    with open(path, encoding="utf-8-sig") as fh:
        names = [line.strip() for line in fh if line.strip() and not line.lstrip().startswith("#")]
    if not names:
        raise ValueError("{}: no names (the file is empty or only has comments)".format(path))
    return names


def _name_patterns(names: Iterable[str]) -> List[Tuple[str, Pattern[str]]]:
    out = []
    for name in names:
        name = " ".join(_fold(name).split())
        if name:
            words = r"\s+".join(re.escape(w) for w in name.split(" "))
            out.append((name, re.compile(r"(?<!\w)" + words + r"(?!\w)")))
    return out


def _personal(text: str, patterns) -> Optional[Tuple[str, str]]:
    if _EMAIL.search(text):
        return RULE_EMAIL, "contains an e-mail address"
    if _has_phone(text):
        return RULE_PHONE, "contains a phone number"
    folded = _fold(text) if patterns else ""
    for _name, pattern in patterns:
        if pattern.search(folded):
            return RULE_NAME, "contains a real name from the names list"
    return None


def personal_data(text: str, names: Iterable[str] = ()) -> Optional[Tuple[str, str]]:
    """(rule, reason) for the first personal datum in `text`, or None. The reason never repeats the datum."""
    return _personal(text, _name_patterns(names))


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            for text in _strings(item):
                yield text
    elif isinstance(value, list):
        for item in value:
            for text in _strings(item):
                yield text


def _texts(example) -> Iterable[Tuple[str, str]]:
    for field in ("messages", "prompt", "chosen", "rejected"):
        for index, message in enumerate(getattr(example, field, None) or ()):
            where = "{}[{}]".format(field, index)
            content = message["content"]
            yield where, content
            if message.get("role") == "assistant":
                try:
                    decoded = json.loads(content)
                except ValueError:
                    continue
                # JSON escapes (\n, \u00e9) hide text in the raw form: screen every decoded string too.
                for text in _strings(decoded):
                    yield where, text


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
