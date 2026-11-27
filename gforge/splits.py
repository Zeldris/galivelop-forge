"""Deterministic partitions (invariant 3): train / val / test decided by the seed and the example's id, never at random.

Each example lands in a partition from `sha256(seed, id)` alone, so the result does not depend on the order of the
examples nor on which other examples are present: adding a new example never moves an old one, and `test`, the
reserve batch of the GVE, never reaches training. The same seed and the same ids always give the same `Split`.
"""
import hashlib
from typing import Iterable, List, Tuple

TRAIN = "train"
VAL = "val"
TEST = "test"
DEFAULT_VAL = 0.1
DEFAULT_TEST = 0.1
_SCALE = 1 << 64


class SplitError(ValueError):
    """Ids or fractions that cannot be partitioned."""


class Split:
    """The three partitions, as sorted tuples of example ids."""

    __slots__ = ("seed", "val_fraction", "test_fraction", "train", "val", "test")

    def __init__(self, seed: str, val_fraction: float, test_fraction: float,
                 train: Tuple[str, ...], val: Tuple[str, ...], test: Tuple[str, ...]) -> None:
        self.seed = seed
        self.val_fraction = val_fraction
        self.test_fraction = test_fraction
        self.train = train
        self.val = val
        self.test = test

    def part(self, name: str) -> Tuple[str, ...]:
        if name not in (TRAIN, VAL, TEST):
            raise KeyError(name)
        return getattr(self, name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Split):
            return NotImplemented
        return (self.seed, self.val_fraction, self.test_fraction, self.train, self.val, self.test) == (
            other.seed, other.val_fraction, other.test_fraction, other.train, other.val, other.test)

    def __repr__(self) -> str:
        return "Split(seed={!r}, train={}, val={}, test={})".format(
            self.seed, len(self.train), len(self.val), len(self.test))


def bucket(seed: str, example_id: str) -> float:
    """A stable number in [0, 1) for this seed and id (length-prefixed so no pair of values can collide)."""
    data = "{}:{}:{}".format(len(seed), seed, example_id).encode("utf-8")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big") / _SCALE


def partition_of(seed: str, example_id: str, val: float = DEFAULT_VAL, test: float = DEFAULT_TEST) -> str:
    """Which partition one id belongs to: [0, test) is test, the next `val` is val, the rest is train."""
    _check_fractions(val, test)
    return _place(bucket(_seed(seed), example_id), val, test)


def split(ids: Iterable[str], seed: str, val: float = DEFAULT_VAL, test: float = DEFAULT_TEST) -> Split:
    """Partition the example ids; a repeated id is an error, since it could be placed in two partitions."""
    seed = _seed(seed)
    _check_fractions(val, test)
    parts = {TRAIN: [], VAL: [], TEST: []}  # type: dict
    seen = set()
    for example_id in ids:
        if not isinstance(example_id, str) or not example_id:
            raise SplitError("example id must be a non-empty string, got {!r}".format(example_id))
        if example_id in seen:
            raise SplitError("duplicate example id {!r}".format(example_id))
        seen.add(example_id)
        parts[_place(bucket(seed, example_id), val, test)].append(example_id)
    result = Split(seed, val, test, tuple(sorted(parts[TRAIN])), tuple(sorted(parts[VAL])), tuple(sorted(parts[TEST])))
    verify(result)
    return result


def verify(result: Split) -> None:
    """Raise SplitError if any id appears in two partitions (a test example must never be in train)."""
    names = (TRAIN, VAL, TEST)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = set(result.part(a)) & set(result.part(b))
            if both:
                raise SplitError("{} ids in both {} and {}, e.g. {!r}".format(len(both), a, b, min(both)))


def _place(value: float, val: float, test: float) -> str:
    if value < test:
        return TEST
    if value < test + val:
        return VAL
    return TRAIN


def _seed(seed: str) -> str:
    if isinstance(seed, bool) or not isinstance(seed, (str, int)) or seed == "":
        raise SplitError("seed must be a non-empty string or an integer, got {!r}".format(seed))
    return str(seed)


def _check_fractions(val: float, test: float) -> None:
    for name, value in (("val", val), ("test", test)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < 1:
            raise SplitError("{} fraction must be a number in [0, 1), got {!r}".format(name, value))
    if val + test >= 1:
        raise SplitError("val + test must leave room for train, got {} + {}".format(val, test))
