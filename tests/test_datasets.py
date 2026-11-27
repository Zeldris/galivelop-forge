"""0.1.0-7: the licence travels (invariant 1) and datasets live in datasets/<target>/<version>/."""
import json
import os
import tempfile
import unittest
from unittest import mock

from gforge import datasets
from gforge.datasets import DatasetError, LicenceError
from gforge.sources.tarkor import SftExample

TEACHER = "groq:llama-3.3-70b-versatile"


def example(i, text="hola", teacher=TEACHER):
    return SftExample("ex-{}".format(i), "cat", teacher, [
        {"role": "system", "content": "s"}, {"role": "user", "content": text},
        {"role": "assistant", "content": json.dumps({"narration": "ok"})}])


EXAMPLES = [example(i) for i in range(60)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name

    def build(self, examples=EXAMPLES, version="0.1.0", **kw):
        args = dict(source="tarkor", source_commit="abc123", date="2026-11-27", seed="s1")
        args.update(kw)
        return datasets.build(self.root, "tarkor.narrator", version, examples, **args)


class LicenceTests(unittest.TestCase):
    def test_nc_dataset_gives_nc_model(self):
        manifests = [{"licence": {"spdx": "CC-BY-4.0", "conditions": ["BY"]}},
                     {"licence": {"spdx": "CC-BY-NC-SA-4.0", "conditions": ["BY", "NC", "SA"]}}]
        self.assertEqual(datasets.model_licence(manifests), "CC-BY-NC-SA-4.0")

    def test_union_of_conditions(self):
        self.assertEqual(datasets.combine(["CC-BY-NC-4.0", "CC-BY-NC-SA-4.0"]), "CC-BY-NC-SA-4.0")
        self.assertEqual(datasets.combine(["CC-BY-4.0", "CC-BY-SA-4.0"]), "CC-BY-SA-4.0")
        self.assertEqual(datasets.combine(["CC0-1.0", "CC-BY-4.0"]), "CC-BY-4.0")

    def test_share_alike_with_non_commercial_fails_closed(self):
        with self.assertRaisesRegex(LicenceError, r"CC-BY-SA-4\.0.*CC-BY-NC-4\.0.*SA does not allow"):
            datasets.combine(["CC-BY-NC-4.0", "CC-BY-SA-4.0"])

    def test_no_licence_or_unknown_fails_closed(self):
        with self.assertRaisesRegex(LicenceError, "no licence given"):
            datasets.combine([])
        with self.assertRaisesRegex(LicenceError, "'WTFPL' is not known"):
            datasets.combine(["WTFPL"])
        with self.assertRaisesRegex(LicenceError, "'MIT' is not known"):
            datasets.model_licence([{"licence": {"spdx": "MIT", "conditions": []}}])

    def test_manifest_without_licence_does_not_validate(self):
        for bad in ({}, {"licence": None}, {"licence": {}}, {"licence": {"spdx": "CC-BY-4.0", "conditions": []}}):
            with self.assertRaises(LicenceError):
                datasets.licence_of(bad)


class BuildTests(Base):
    def test_record_str_slots_is_one_slot(self):
        class One:
            __slots__ = "id"

            def __init__(self):
                self.id = "x"

        self.assertEqual(datasets._record(One()), {"id": "x"})

    def test_fsync_failure_after_publish_does_not_raise(self):
        real = datasets._sync_dir
        calls = []

        def flaky(path):
            calls.append(path)
            if os.path.exists(os.path.join(self.root, "tarkor.narrator", "0.1.0")):
                raise OSError("fsync failed")
            real(path)

        with mock.patch.object(datasets, "_sync_dir", flaky):
            final = self.build()
        self.assertTrue(os.path.isfile(os.path.join(final, "manifest.json")))
        self.assertGreaterEqual(len(calls), 2)

    def test_layout_and_licence_written(self):
        path = self.build()
        self.assertEqual(path, os.path.join(self.root, "tarkor.narrator", "0.1.0"))
        self.assertEqual(sorted(os.listdir(path)),
                         ["LICENSE", "manifest.json", "test.jsonl", "train.jsonl", "val.jsonl"])
        manifest = datasets.verify(path)
        self.assertEqual(manifest["licence"]["spdx"], "CC-BY-NC-SA-4.0")
        self.assertEqual(manifest["licence"]["conditions"], ["BY", "NC", "SA"])
        self.assertEqual(manifest["teachers"], [TEACHER])
        with open(os.path.join(path, "LICENSE"), encoding="utf-8") as handle:
            self.assertIn("CC-BY-NC-SA-4.0", handle.read())

    def test_licence_cannot_be_weaker_than_content_licence(self):
        manifest = datasets.read_manifest(self.build(source_licences=["CC0-1.0"]))
        self.assertEqual(manifest["licence"]["spdx"], "CC-BY-NC-SA-4.0")

    def test_same_input_same_bytes(self):
        a = self.build(version="a")
        b = self.build(version="b")
        for name in ("train.jsonl", "val.jsonl", "test.jsonl"):
            with open(os.path.join(a, name), "rb") as x, open(os.path.join(b, name), "rb") as y:
                self.assertEqual(x.read(), y.read())
        self.assertEqual(datasets.read_manifest(a)["dataset_hash"], datasets.read_manifest(b)["dataset_hash"])

    def test_version_is_never_overwritten(self):
        self.build()
        with self.assertRaisesRegex(DatasetError, "already exists"):
            self.build()
        self.assertEqual(datasets.find(self.root, "tarkor.narrator"), ["0.1.0"])

    def test_date_must_be_iso(self):
        for bad in ("27/11/2026", "2026-13-01", "2026-1-1", "2026-11-27T10:00", "hoy"):
            with self.assertRaisesRegex(DatasetError, "must be ISO YYYY-MM-DD"):
                self.build(date=bad)
        self.assertEqual(datasets.find(self.root, "tarkor.narrator"), [])

    def test_failed_build_leaves_no_temporary_directory(self):
        with mock.patch.object(datasets, "_sync_dir", side_effect=RuntimeError("boom")):
            with self.assertRaisesRegex(RuntimeError, "boom"):
                self.build()
        self.assertEqual(os.listdir(os.path.join(self.root, "tarkor.narrator")), [])

    def test_files_and_directory_are_fsynced(self):
        with mock.patch("os.fsync") as fsync:
            self.build()
        self.assertGreaterEqual(fsync.call_count, 5)  # 3 partitions + LICENSE + manifest (+ directories)

    def test_empty_existing_version_directory_is_replaced_on_posix(self):
        if os.name != "posix":
            self.skipTest("Windows refuses to replace an existing directory")
        os.makedirs(os.path.join(self.root, "tarkor.narrator", "0.1.0"))
        final = self.build()
        self.assertTrue(os.path.isfile(os.path.join(final, "manifest.json")))

    def test_existing_version_is_detected_at_rename_not_before(self):
        final = os.path.join(self.root, "tarkor.narrator", "0.1.0")
        real = os.rename

        def racing(src, dst):  # another process publishes the version between our work and our rename
            os.makedirs(os.path.join(dst, "x"))
            return real(src, dst)
        with mock.patch("os.rename", racing):
            with self.assertRaisesRegex(DatasetError, "already exists"):
                self.build()
        self.assertEqual(os.listdir(os.path.join(final)), ["x"])
        self.assertEqual(os.listdir(os.path.dirname(final)), ["0.1.0"])

    def test_record_includes_inherited_slots(self):
        class Base_(object):
            __slots__ = ("id", "a")

        class Child(Base_):
            __slots__ = ("b",)
        c = Child()
        c.id, c.a, c.b = "i", 1, 2
        self.assertEqual(datasets._record(c), {"id": "i", "a": 1, "b": 2})

    def test_rejected_examples_are_listed_without_their_text(self):
        bad = example(999, text="escribeme a alguien@example.com")
        path = self.build(EXAMPLES + [bad])
        manifest = datasets.read_manifest(path)
        self.assertEqual([r["id"] for r in manifest["rejected"]], ["ex-999"])
        for name in os.listdir(path):
            with open(os.path.join(path, name), encoding="utf-8") as handle:
                self.assertNotIn("alguien@example.com", handle.read())

    def test_closed_teacher_is_rejected(self):
        manifest = datasets.read_manifest(self.build(EXAMPLES + [example(998, teacher="openai:gpt-4o")]))
        self.assertEqual([r["id"] for r in manifest["rejected"]], ["ex-998"])

    def test_nothing_left_writes_nothing(self):
        with self.assertRaisesRegex(DatasetError, "no example left"):
            self.build([example(1, teacher="openai:gpt-4o")])
        self.assertEqual(os.listdir(self.root), [])

    def test_bad_names_and_missing_provenance(self):
        with self.assertRaisesRegex(DatasetError, "target"):
            datasets.build(self.root, "../x", "1", EXAMPLES, "t", "c", "d", "s")
        with self.assertRaisesRegex(DatasetError, "version"):
            self.build(version="Bad/Version")
        with self.assertRaisesRegex(DatasetError, "source_commit is required"):
            self.build(source_commit="")

    def test_verify_detects_tampering_and_missing_licence(self):
        path = self.build()
        with open(os.path.join(path, "train.jsonl"), "a", encoding="utf-8") as handle:
            handle.write('{"id":"ex-x"}\n')
        with self.assertRaisesRegex(DatasetError, "ids differ"):
            datasets.verify(path)
        path = self.build(version="0.2.0")
        manifest_file = os.path.join(path, "manifest.json")
        with open(manifest_file, encoding="utf-8") as handle:
            manifest = json.load(handle)
        del manifest["licence"]
        with open(manifest_file, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle)
        with self.assertRaises(LicenceError):
            datasets.read_manifest(path)

    def _edit_manifest(self, path, change):
        manifest_file = os.path.join(path, "manifest.json")
        with open(manifest_file, encoding="utf-8") as handle:
            manifest = json.load(handle)
        change(manifest)
        with open(manifest_file, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle)

    def test_verify_rejects_partition_keys_other_than_train_val_test(self):
        path = self.build()
        self._edit_manifest(path, lambda m: m["partitions"].update({"../../x": []}))
        with self.assertRaisesRegex(DatasetError, "partitions must be exactly train, val, test"):
            datasets.verify(path)

    def test_verify_rejects_test_example_leaked_into_train(self):
        path = self.build()
        with open(os.path.join(path, "test.jsonl"), encoding="utf-8") as handle:
            leaked = handle.readline()
        leaked_id = json.loads(leaked)["id"]
        with open(os.path.join(path, "train.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(leaked)
        self._edit_manifest(path, lambda m: m["partitions"]["train"].append(leaked_id))
        with self.assertRaisesRegex(DatasetError, "not disjoint"):
            datasets.verify(path)

    def test_verify_requires_matching_licence_notice(self):
        path = self.build()
        os.remove(os.path.join(path, "LICENSE"))
        with self.assertRaisesRegex(DatasetError, "missing licence notice"):
            datasets.verify(path)
        path = self.build(version="0.2.0")
        with open(os.path.join(path, "LICENSE"), "w", encoding="utf-8") as handle:
            handle.write("CC0\n")
        with self.assertRaisesRegex(DatasetError, "LICENSE differs"):
            datasets.verify(path)

    def test_verify_recomputes_dataset_hash(self):
        path = self.build()
        self._edit_manifest(path, lambda m: m.update({"dataset_hash": "0" * 64}))
        with self.assertRaisesRegex(DatasetError, "dataset_hash differs"):
            datasets.verify(path)

    def test_verify_reports_malformed_row_with_file_and_line(self):
        for bad in ("not json", "[1]", '{"no":"id"}'):
            path = self.build(version="v-{}".format(len(bad)))
            with open(os.path.join(path, "val.jsonl"), "a", encoding="utf-8") as handle:
                handle.write(bad + "\n")
            with self.assertRaisesRegex(DatasetError, r"val\.jsonl:\d+: malformed row"):
                datasets.verify(path)

    def test_licence_conditions_must_be_list_of_strings(self):
        manifest = {"licence": {"spdx": "CC-BY-4.0", "conditions": [1, "BY"]}}
        with self.assertRaisesRegex(LicenceError, "list of strings"):
            datasets.licence_of(manifest)
        manifest["licence"]["conditions"] = "BY"
        with self.assertRaisesRegex(LicenceError, "list of strings"):
            datasets.licence_of(manifest)


if __name__ == "__main__":
    unittest.main()
