"""Which teachers forge accepts (invariant 9, ADR 0007): only open ones whose terms allow training on their outputs.

A teacher id is `<host>:<model>` as Tarkor writes it (`groq:llama-3.3-70b-versatile`); the host only serves the
model, so the decision is made on the model (the part after the first `:`, lower case, last `/` segment). The
list fails closed: a model that matches no pattern is rejected, the same as a closed one, so a new teacher enters
only when someone adds it here with its licence.
"""
from fnmatch import fnmatchcase
from typing import Optional, Sequence, Tuple

# (pattern, why) — terms that forbid training other models on the outputs.
CLOSED_TEACHERS: Sequence[Tuple[str, str]] = (
    ("claude*", "Anthropic's terms forbid training models on Claude outputs"),
    ("gpt-[0-9]*", "OpenAI's terms forbid training competing models on its outputs"),
    ("chatgpt*", "OpenAI's terms forbid training competing models on its outputs"),
    ("o[1-9]*", "OpenAI's terms forbid training competing models on its outputs"),
    ("gemini*", "Google's Gemini API terms forbid developing competing models with its outputs"),
)

# (pattern, licence) — open weights whose licence allows training on the outputs.
OPEN_TEACHERS: Sequence[Tuple[str, str]] = (
    ("*llama-3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("*llama3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("*llama-4*", "Llama 4 Community License (outputs may train other models, with attribution)"),
    ("*deepseek-r1*", "MIT (DeepSeek-R1 allows distillation explicitly)"),
    ("*deepseek-v3*", "MIT code, DeepSeek model licence allowing derived models"),
    ("*gpt-oss*", "Apache 2.0"),
)


def model_of(teacher: str) -> str:
    """The model part of a teacher id: after the first `:`, last `/` segment, lower case."""
    model = teacher.split(":", 1)[1] if ":" in teacher else teacher
    return model.rsplit("/", 1)[-1].strip().lower()


def teacher_rejection(teacher: Optional[str]) -> Optional[str]:
    """None when the teacher is on the open list; otherwise why it is rejected."""
    if not isinstance(teacher, str) or not teacher.strip():
        return "no teacher declared"
    model = model_of(teacher)
    if not model:
        return "teacher {!r} names no model".format(teacher)
    for pattern, why in CLOSED_TEACHERS:
        if fnmatchcase(model, pattern):
            return "teacher {!r} is closed: {}".format(teacher, why)
    for pattern, _licence in OPEN_TEACHERS:
        if fnmatchcase(model, pattern):
            return None
    return "teacher {!r} is not on the open-teacher list (gforge/teachers.py)".format(teacher)
