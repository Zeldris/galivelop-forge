"""Tarkor source: reads what the game's dataset scripts export; never runs them.

Formats read (World-Maker-Fantasy, backend/, see docs/sources/tarkor.md):

- distillation: `output/distillation-dataset/<category>.jsonl`, one SFT record per line,
  `{"id", "category", "provider", "messages": [system, user, assistant]}`; the assistant
  content is a NarrationResult serialised as a JSON string. `train.jsonl` and `eval.jsonl`
  are the game's own split and are skipped: forge splits by itself (invariant 3).
- DPO: `output/dpo-dataset/live-dpo.jsonl`, `{"id", "provider", "prompt": [system, user],
  "chosen": [assistant], "rejected": [assistant]}`. A pair made by the synthetic generator
  carries `<!-- scenario-id: <id> -->` at the end of the user content; any other pair comes
  from live play and may carry text typed by a player (invariant 2 filters it later).

A malformed line is never skipped: it raises SourceError with the file, the line and why.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

SOURCE = "tarkor"
TARGET = "tarkor.narrator"
GAME_SPLIT_FILES = ("train.jsonl", "eval.jsonl")
ORIGIN_SYNTHETIC = "synthetic"
ORIGIN_LIVE = "live"

_SCENARIO_MARK = re.compile(r"\n*<!-- scenario-id: ([^\s>]+) -->\s*$")


class SourceError(ValueError):
    """A Tarkor export that does not have the expected shape."""

    def __init__(self, path: str, line: int, reason: str) -> None:
        self.path = path
        self.line = line
        self.reason = reason
        super().__init__(str(self))

    def __reduce__(self) -> Any:  # default pickling replays args=(message,) into the 3-argument init; __dict__ keeps add_note notes
        return (type(self), (self.path, self.line, self.reason), self.__dict__)

    def __str__(self) -> str:
        where = self.path if self.line <= 0 else "{}:{}".format(self.path, self.line)
        return "{}: {}".format(where, self.reason)


class SftExample:
    """One distillation record: the teacher's narration for a scenario."""

    __slots__ = ("id", "category", "teacher", "messages", "origin")

    def __init__(self, id: str, category: str, teacher: str, messages: List[Dict[str, str]]) -> None:
        self.id = id
        self.category = category
        self.teacher = teacher
        self.messages = messages
        self.origin = ORIGIN_SYNTHETIC

    def __repr__(self) -> str:
        return "SftExample(id={!r}, category={!r}, teacher={!r})".format(self.id, self.category, self.teacher)


class PreferenceExample:
    """One DPO pair: the teacher's answer (chosen) against the local narrator's (rejected)."""

    __slots__ = ("id", "teacher", "prompt", "chosen", "rejected", "scenario_id", "origin")

    def __init__(
        self,
        id: str,
        teacher: str,
        prompt: List[Dict[str, str]],
        chosen: List[Dict[str, str]],
        rejected: List[Dict[str, str]],
        scenario_id: Optional[str],
    ) -> None:
        self.id = id
        self.teacher = teacher
        self.prompt = prompt
        self.chosen = chosen
        self.rejected = rejected
        self.scenario_id = scenario_id
        self.origin = ORIGIN_LIVE if scenario_id is None else ORIGIN_SYNTHETIC

    def __repr__(self) -> str:
        return "PreferenceExample(id={!r}, teacher={!r}, origin={!r})".format(self.id, self.teacher, self.origin)


def _lines(path: str) -> Iterator[Tuple[int, Dict[str, Any]]]:
    number = 0
    try:
        with open(path, encoding="utf-8") as fh:
            for number, raw in enumerate(fh, 1):
                if not raw.strip():
                    continue
                try:
                    record = json.loads(raw)
                except ValueError as exc:
                    raise SourceError(path, number, "not valid JSON ({})".format(exc))
                if not isinstance(record, dict):
                    raise SourceError(path, number, "a record must be a JSON object")
                yield number, record
    except UnicodeDecodeError as exc:
        raise SourceError(path, number + 1, "not valid UTF-8 ({})".format(exc))
    except OSError as exc:
        raise SourceError(path, number, "cannot be read ({})".format(exc.strerror or exc))


def _text(record: Dict[str, Any], key: str, path: str, line: int) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SourceError(path, line, "field {!r} must be a non-empty string".format(key))
    return value


def _messages(value: Any, roles: Sequence[str], key: str, path: str, line: int) -> List[Dict[str, str]]:
    if not isinstance(value, list) or len(value) != len(roles):
        raise SourceError(path, line, "{!r} must be a list of {} messages ({})".format(key, len(roles), ", ".join(roles)))
    out = []
    for index, (message, role) in enumerate(zip(value, roles)):
        if not isinstance(message, dict) or message.get("role") != role:
            raise SourceError(path, line, "{}[{}] must have role {!r}".format(key, index, role))
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise SourceError(path, line, "{}[{}].content must be a non-empty string".format(key, index))
        out.append({"role": role, "content": content})
    return out


def _narration(content: str, where: str, path: str, line: int, allow_empty: bool = False) -> None:
    """The assistant content must be a NarrationResult: narration (str) and newFacts (list of str).

    An empty narration is refused unless `allow_empty`: a DPO `rejected` may be the empty output of the local narrator.
    """
    try:
        result = json.loads(content)
    except ValueError:
        raise SourceError(path, line, "{} is not a JSON NarrationResult".format(where))
    if not isinstance(result, dict) or not isinstance(result.get("narration"), str):
        raise SourceError(path, line, "{} has no string 'narration'".format(where))
    if not allow_empty and not result["narration"].strip():
        raise SourceError(path, line, "{} has an empty 'narration'".format(where))
    facts = result.get("newFacts")
    if not isinstance(facts, list) or not all(isinstance(f, str) for f in facts):
        raise SourceError(path, line, "{} has no 'newFacts' list of strings".format(where))


def _no_duplicate(seen: Dict[str, str], id: str, path: str, line: int) -> None:
    if id in seen:
        raise SourceError(path, line, "id {!r} repeated (first at {})".format(id, seen[id]))
    seen[id] = "{}:{}".format(path, line)


def read_distillation(directory: str) -> List[SftExample]:
    """Read every `<category>.jsonl` of a distillation export, in name order (deterministic)."""
    if not os.path.isdir(directory):
        raise SourceError(directory, 0, "distillation export directory not found")
    names = sorted(n for n in os.listdir(directory) if n.lower().endswith(".jsonl") and n.lower() not in GAME_SPLIT_FILES
        and os.path.isfile(os.path.join(directory, n)))
    if not names:
        raise SourceError(directory, 0, "no <category>.jsonl files (train/eval are skipped)")
    seen: Dict[str, str] = {}
    examples = []
    for name in names:
        path = os.path.join(directory, name)
        file_category = name[: -len(".jsonl")]
        for line, record in _lines(path):
            id = _text(record, "id", path, line)
            category = _text(record, "category", path, line)
            if category != file_category:
                raise SourceError(path, line, "category {!r} does not match the file {!r}".format(category, name))
            teacher = _text(record, "provider", path, line)
            messages = _messages(record.get("messages"), ("system", "user", "assistant"), "messages", path, line)
            _narration(messages[2]["content"], "messages[2].content", path, line)
            _no_duplicate(seen, id, path, line)
            examples.append(SftExample(id, category, teacher, messages))
    return examples


def read_dpo(path: str) -> List[PreferenceExample]:
    """Read a DPO export (`live-dpo.jsonl`) in file order."""
    if not os.path.isfile(path):
        raise SourceError(path, 0, "DPO export file not found")
    seen: Dict[str, str] = {}
    examples = []
    for line, record in _lines(path):
        id = _text(record, "id", path, line)
        teacher = _text(record, "provider", path, line)
        prompt = _messages(record.get("prompt"), ("system", "user"), "prompt", path, line)
        chosen = _messages(record.get("chosen"), ("assistant",), "chosen", path, line)
        rejected = _messages(record.get("rejected"), ("assistant",), "rejected", path, line)
        _narration(chosen[0]["content"], "chosen[0].content", path, line)
        _narration(rejected[0]["content"], "rejected[0].content", path, line, allow_empty=True)
        match = _SCENARIO_MARK.search(prompt[1]["content"])
        scenario_id = None
        if match:
            scenario_id = match.group(1)
            prompt[1]["content"] = prompt[1]["content"][: match.start()]
            if not prompt[1]["content"].strip():
                raise SourceError(path, line, "prompt[1].content is empty after the scenario mark")
        _no_duplicate(seen, id, path, line)
        examples.append(PreferenceExample(id, teacher, prompt, chosen, rejected, scenario_id))
    return examples
