"""Datasets in the repo (ADR 0002) and the licence that travels with them (invariant 1).

A dataset lives in `datasets/<target>/<version>/`: one `<partition>.jsonl` per partition, a `LICENSE` notice and
`manifest.json` (`gforge.dataset/0`, provisional until gart validates it: 0.1.0-3). The licence is never optional:
`build` always writes it, `read_manifest` rejects a manifest without it, and a model's licence is the most
restrictive of its datasets' (`combine`), so a Tarkor (CC BY-NC-SA) dataset can never yield a model without NC.

Licences are modelled by their conditions (attribution, non-commercial, share-alike). Only the Creative Commons
family is known; anything else fails closed until someone adds it to `LICENCES` with its conditions.
"""
import hashlib
import json
import os
import re
import shutil
import tempfile
from typing import Any, Dict, FrozenSet, Iterable, List, Sequence

from gforge import filters, splits

SCHEMA = "gforge.dataset/0"
MANIFEST = "manifest.json"
LICENSE_FILE = "LICENSE"
BY, NC, SA = "BY", "NC", "SA"

# SPDX id -> (conditions, url of the legal text). Only these combine; an unknown id raises LicenceError.
LICENCES = {
    "CC0-1.0": (frozenset(), "https://creativecommons.org/publicdomain/zero/1.0/legalcode"),
    "CC-BY-4.0": (frozenset([BY]), "https://creativecommons.org/licenses/by/4.0/legalcode"),
    "CC-BY-SA-4.0": (frozenset([BY, SA]), "https://creativecommons.org/licenses/by-sa/4.0/legalcode"),
    "CC-BY-NC-4.0": (frozenset([BY, NC]), "https://creativecommons.org/licenses/by-nc/4.0/legalcode"),
    "CC-BY-NC-SA-4.0": (frozenset([BY, NC, SA]), "https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode"),
}
CONTENT_LICENCE = "CC-BY-NC-SA-4.0"  # ADR 0002: every dataset in this repo is content under this licence.

_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class LicenceError(ValueError):
    """A missing, unknown or unmergeable licence."""


class DatasetError(ValueError):
    """A dataset that cannot be built, written or read back."""


def conditions(spdx: Any) -> FrozenSet[str]:
    if not isinstance(spdx, str) or spdx not in LICENCES:
        raise LicenceError("licence {!r} is not known; add it to gforge.datasets.LICENCES with its conditions "
                           "(known: {})".format(spdx, ", ".join(sorted(LICENCES))))
    return LICENCES[spdx][0]


def combine(spdx_ids: Iterable[str]) -> str:
    """The most restrictive licence of all: the union of conditions (invariant 1). Empty input is an error."""
    ids = list(spdx_ids)
    if not ids:
        raise LicenceError("no licence given: a dataset or model without a licence is not valid")
    union = frozenset().union(*(conditions(i) for i in ids))
    for spdx, (known, _url) in LICENCES.items():
        if known == union:
            return spdx
    raise LicenceError("no known licence has the conditions {} of {}".format(sorted(union), ids))


def model_licence(manifests: Sequence[Dict[str, Any]]) -> str:
    """The licence a model trained on these datasets inherits (invariant 1)."""
    return combine(licence_of(m) for m in manifests)


def licence_of(manifest: Dict[str, Any]) -> str:
    """The SPDX id of a manifest; a manifest without a valid licence does not validate."""
    licence = manifest.get("licence") if isinstance(manifest, dict) else None
    spdx = licence.get("spdx") if isinstance(licence, dict) else None
    conditions(spdx)
    listed = licence.get("conditions", ())
    if not isinstance(listed, (list, tuple)) or not all(isinstance(c, str) for c in listed):
        raise LicenceError("manifest conditions must be a list of strings, got {!r}".format(listed))
    if sorted(listed) != sorted(conditions(spdx)):
        raise LicenceError("manifest conditions {} do not match {}".format(licence.get("conditions"), spdx))
    return spdx


def _name(kind: str, value: Any) -> str:
    if not isinstance(value, str) or not _NAME.match(value):
        raise DatasetError("{} {!r} must match {}".format(kind, value, _NAME.pattern))
    return value


def _record(example: Any) -> Dict[str, Any]:
    return {slot: getattr(example, slot) for slot in example.__slots__}


def _canonical(record: Dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build(
    root: str,
    target: str,
    version: str,
    examples: Sequence[Any],
    source: str,
    source_commit: str,
    date: str,
    seed: Any,
    source_licences: Sequence[str] = (CONTENT_LICENCE,),
    names: Sequence[str] = (),
    val: float = splits.DEFAULT_VAL,
    test: float = splits.DEFAULT_TEST,
) -> str:
    """Screen, split and write `<root>/<target>/<version>/`; return its path. A version is never overwritten.

    The licence is `combine` of the repo's content licence and the sources'. Rejected examples are listed in the
    manifest by id and rule only: their text (maybe personal data) is never written.
    """
    _name("target", target)
    _name("version", version)
    for label, value in (("source", source), ("source_commit", source_commit), ("date", date)):
        if not isinstance(value, str) or not value.strip():
            raise DatasetError("{} is required (provenance)".format(label))
    spdx = combine([CONTENT_LICENCE] + list(source_licences))
    kept, rejections = filters.screen(examples, names)
    if not kept:
        raise DatasetError("no example left after the filters ({} rejected)".format(len(rejections)))
    result = splits.split([e.id for e in kept], seed, val, test)
    final = os.path.join(root, target, version)
    if os.path.exists(final):
        raise DatasetError("{} already exists: a published version is never overwritten, use a new version".format(final))
    by_id = {e.id: _record(e) for e in kept}
    lines = {id_: _canonical(r) for id_, r in by_id.items()}
    manifest = {
        "schema": SCHEMA,
        "target": target,
        "version": version,
        "licence": {"spdx": spdx, "conditions": sorted(conditions(spdx)), "url": LICENCES[spdx][1]},
        "provenance": {"source": source, "commit": source_commit, "date": date},
        "teachers": sorted({e.teacher for e in kept}),
        "seed": str(result.seed),
        "fractions": {"val": result.val_fraction, "test": result.test_fraction},
        "partitions": {name: list(result.part(name)) for name in (splits.TRAIN, splits.VAL, splits.TEST)},
        "examples": {id_: _sha(lines[id_]) for id_ in sorted(lines)},
        "rejected": [{"id": r.id, "rule": r.rule} for r in rejections],
    }
    manifest["dataset_hash"] = _hash_of(manifest["examples"])
    os.makedirs(os.path.join(root, target), exist_ok=True)
    work = tempfile.mkdtemp(prefix=".build-", dir=os.path.join(root, target))
    try:
        for name in (splits.TRAIN, splits.VAL, splits.TEST):
            with open(os.path.join(work, name + ".jsonl"), "w", encoding="utf-8", newline="\n") as handle:
                for id_ in result.part(name):
                    handle.write(lines[id_] + "\n")
        with open(os.path.join(work, LICENSE_FILE), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(_notice(manifest))
        with open(os.path.join(work, MANIFEST), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
        os.rename(work, final)
    except BaseException:
        shutil.rmtree(work, ignore_errors=True)
        raise
    return final


def _notice(manifest: Dict[str, Any]) -> str:
    licence = manifest["licence"]
    return (
        "Content of dataset {target} {version}: {spdx}\n"
        "{url}\n\n"
        "Source: {source} ({commit}, {date}). Models trained on this dataset inherit these conditions: {conds}.\n"
    ).format(
        target=manifest["target"], version=manifest["version"], spdx=licence["spdx"], url=licence["url"],
        source=manifest["provenance"]["source"], commit=manifest["provenance"]["commit"],
        date=manifest["provenance"]["date"], conds=", ".join(licence["conditions"]) or "none",
    )


def read_manifest(path: str) -> Dict[str, Any]:
    """Read `<dataset dir>/manifest.json`; fail if the schema or the licence is missing or wrong."""
    try:
        with open(os.path.join(path, MANIFEST), encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, ValueError) as error:
        raise DatasetError("{}: cannot read manifest: {}".format(path, error))
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise DatasetError("{}: not a {} manifest".format(path, SCHEMA))
    licence_of(manifest)
    return manifest


def _hash_of(examples: Dict[str, str]) -> str:
    return _sha("\n".join("{} {}".format(i, h) for i, h in examples.items()))


def _row_id(file: str, number: int, row: str) -> str:
    """The id of one jsonl row, parsed once; any malformed row is a DatasetError with file and line."""
    try:
        record = json.loads(row)
        if not isinstance(record, dict):
            raise TypeError("row is {} not an object".format(type(record).__name__))
        id_ = record["id"]
        if not isinstance(id_, str):
            raise TypeError("id {!r} is not a string".format(id_))
        return id_
    except (ValueError, KeyError, TypeError) as error:
        raise DatasetError("{}:{}: malformed row: {!r}".format(file, number, error))


def verify(path: str) -> Dict[str, Any]:
    """Read the manifest and check partitions, licence notice and hashes against what it lists."""
    manifest = read_manifest(path)
    names = (splits.TRAIN, splits.VAL, splits.TEST)
    partitions = manifest.get("partitions")
    if not isinstance(partitions, dict) or sorted(partitions) != sorted(names):
        raise DatasetError("{}: manifest partitions must be exactly {}".format(path, ", ".join(names)))
    for name in names:
        ids = partitions[name]
        if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
            raise DatasetError("{}: partition {} must be a list of ids".format(path, name))
    seed = str(manifest.get("seed"))
    fractions = manifest.get("fractions") or {}
    try:
        splits.verify(splits.Split(seed, fractions.get("val"), fractions.get("test"),
                                   *(tuple(partitions[n]) for n in names)))
    except splits.SplitError as error:
        raise DatasetError("{}: partitions are not disjoint: {}".format(path, error))
    try:
        with open(os.path.join(path, LICENSE_FILE), encoding="utf-8") as handle:
            notice = handle.read()
    except OSError as error:
        raise DatasetError("{}: missing licence notice: {}".format(path, error))
    try:
        expected = _notice(manifest)
    except (KeyError, TypeError, AttributeError) as error:
        raise DatasetError("{}: manifest lacks provenance for the notice: {!r}".format(path, error))
    if notice != expected:
        raise DatasetError("{}: {} differs from the manifest's licence".format(path, LICENSE_FILE))
    seen = {}  # type: Dict[str, str]
    for name in names:
        file = os.path.join(path, name + ".jsonl")
        try:
            with open(file, encoding="utf-8") as handle:
                rows = [line.rstrip("\n") for line in handle]
        except OSError as error:
            raise DatasetError("{}: {}".format(file, error))
        ids = [_row_id(file, n, r) for n, r in enumerate(rows, 1)]
        if ids != partitions[name]:
            raise DatasetError("{}: ids differ from the manifest's partition {}".format(file, name))
        for id_, row in zip(ids, rows):
            seen[id_] = _sha(row)
    if seen != manifest["examples"]:
        raise DatasetError("{}: example hashes differ from the manifest".format(path))
    if manifest.get("dataset_hash") != _hash_of(manifest["examples"]):
        raise DatasetError("{}: dataset_hash differs from the example hashes".format(path))
    return manifest


def find(root: str, target: str) -> List[str]:
    """Versions of a target present under `root`, sorted."""
    base = os.path.join(root, _name("target", target))
    if not os.path.isdir(base):
        return []
    return sorted(v for v in os.listdir(base) if _NAME.match(v) and os.path.isfile(os.path.join(base, v, MANIFEST)))
