"""Which teachers forge accepts (invariant 9, ADR 0007): only open ones whose terms allow training on their outputs.

A teacher id is `<host>:<model>` as Tarkor writes it (`groq:llama-3.3-70b-versatile`); the host only serves the
model, so the decision is made on the model (the part after the first `:`, lower case, last `/` segment). The
list fails closed: a model that matches no pattern is rejected, the same as a closed one, so a new teacher enters
only when someone adds it here with its licence.

Names come as `x-y` or, from Ollama, as `x:tag` (`deepseek-r1:70b`): the tag keeps its suffix after `model_of`, so an
exclusion has to cover both forms or an open pattern (`deepseek-r1*`) lets the second through.
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

# Models with a licence of their own: rejected until someone adds them with that licence. Checked before OPEN_TEACHERS.
EXCLUDED_TEACHERS: Sequence[Tuple[str, str]] = (
    ("*llama-3.2*vision*", "Llama 3.2 vision has its own licence (not covered by the 3.1+ list)"),
    ("*llama3.2*vision*", "Llama 3.2 vision has its own licence (not covered by the 3.1+ list)"),
    ("*deepseek-r1-distill-llama*", "DeepSeek-R1-Distill-Llama carries the Llama licence of its base"),
    ("deepseek-r1:70b*", "Ollama deepseek-r1:70b is DeepSeek-R1-Distill-Llama-70B (Llama licence of its base)"),
    ("deepseek-r1:8b*", "Ollama deepseek-r1:8b may be DeepSeek-R1-Distill-Llama-8B (Llama licence of its base)"),
)

# Patterns are anchored at the start of the model name: `model_of` already drops any provider or organisation
# prefix (`ollama/`, `hf/`, `org/`), so a name that merely contains the substring does not enter.
# (pattern, licence) — open weights whose licence allows training on the outputs.
OPEN_TEACHERS: Sequence[Tuple[str, str]] = (
    ("llama-3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("llama3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("meta-llama-3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("meta-llama3.[123]*", "Llama 3.1+ Community License (outputs may train other models, with attribution)"),
    ("meta-llama-4*", "Llama 4 Community License (outputs may train other models, with attribution)"),
    ("llama-4*", "Llama 4 Community License (outputs may train other models, with attribution)"),
    ("deepseek-r1*", "MIT (DeepSeek-R1 allows distillation explicitly)"),
    ("deepseek-v3*", "MIT code, DeepSeek model licence allowing derived models"),
    ("gpt-oss*", "Apache 2.0"),
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
    for pattern, why in EXCLUDED_TEACHERS:
        if fnmatchcase(model, pattern):
            return "teacher {!r} is excluded: {}".format(teacher, why)
    for pattern, _licence in OPEN_TEACHERS:
        if fnmatchcase(model, pattern):
            return None
    return "teacher {!r} is not on the open-teacher list (gforge/teachers.py)".format(teacher)
