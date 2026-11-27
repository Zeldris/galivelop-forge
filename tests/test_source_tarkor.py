"""0.1.0-4: the Tarkor source reads the distillation and DPO exports and fails closed on a bad line."""
import json
import pickle
import os
import tempfile
import unittest

from gforge.sources.tarkor import (
    ORIGIN_LIVE,
    ORIGIN_SYNTHETIC,
    SourceError,
    read_distillation,
    read_dpo,
)

NARRATION = json.dumps({"narration": "La niebla cubre el paso.", "newFacts": ["El paso está cerrado."]})


def sft(id, category, assistant=NARRATION):
    return {
        "id": id,
        "category": category,
        "provider": "groq:llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres el narrador."},
            {"role": "user", "content": "Gorhorn mira al norte."},
            {"role": "assistant", "content": assistant},
        ],
    }


def dpo(id, user="Gorhorn mira al norte.", chosen=NARRATION, rejected=NARRATION):
    return {
        "id": id,
        "provider": "gemini:x",
        "prompt": [{"role": "system", "content": "Eres el narrador."}, {"role": "user", "content": user}],
        "chosen": [{"role": "assistant", "content": chosen}],
        "rejected": [{"role": "assistant", "content": rejected}],
    }


class Export(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, records):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            for record in records:
                fh.write((record if isinstance(record, str) else json.dumps(record, ensure_ascii=False)) + "\n")
        return path

    def assertReason(self, fn, *needles):
        with self.assertRaises(SourceError) as cm:
            fn()
        for needle in needles:
            self.assertIn(needle, str(cm.exception))
        return cm.exception


class Distillation(Export):
    def test_reads_categories_in_name_order_and_skips_the_game_split(self):
        self.write("viaje.jsonl", [sft("v1", "viaje")])
        self.write("combate.jsonl", [sft("c1", "combate"), sft("c2", "combate")])
        self.write("train.jsonl", [sft("c1", "combate")])
        self.write("eval.jsonl", [sft("v1", "viaje")])
        examples = read_distillation(self.dir)
        self.assertEqual([e.id for e in examples], ["c1", "c2", "v1"])
        self.assertEqual(examples[0].teacher, "groq:llama-3.3-70b-versatile")
        self.assertEqual([m["role"] for m in examples[0].messages], ["system", "user", "assistant"])
        self.assertEqual(examples[0].origin, ORIGIN_SYNTHETIC)

    def test_category_that_does_not_match_its_file(self):
        self.write("viaje.jsonl", [sft("v1", "combate")])
        self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl:1", "does not match the file")

    def test_assistant_that_is_not_a_narration(self):
        self.write("viaje.jsonl", [sft("v1", "viaje"), sft("v2", "viaje", assistant='{"text": "x"}')])
        self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl:2", "no string 'narration'")

    def test_empty_or_blank_narration_is_rejected(self):
        for blank in ("", "   \n"):
            self.write("viaje.jsonl", [sft("v1", "viaje", assistant=json.dumps({"narration": blank, "newFacts": []}))])
            self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl:1", "empty 'narration'")

    def test_dpo_empty_narration_is_refused_in_chosen_and_accepted_in_rejected(self):
        blank = json.dumps({"narration": "", "newFacts": []})
        path = os.path.join(self.dir, "live-dpo.jsonl")
        self.write("live-dpo.jsonl", [dpo("d1", chosen=blank)])
        self.assertReason(lambda: read_dpo(path), "live-dpo.jsonl:1", "chosen[0].content has an empty 'narration'")
        self.write("live-dpo.jsonl", [dpo("d1", rejected=blank)])
        self.assertEqual([e.id for e in read_dpo(path)], ["d1"])

    def test_extension_is_case_insensitive(self):
        self.write("Cat.JSONL", [sft("a", "Cat")])
        self.write("Train.JSONL", [sft("t", "combate")])
        self.assertEqual([e.id for e in read_distillation(self.dir)], ["a"])

    def test_repeated_id_across_files(self):
        self.write("combate.jsonl", [sft("x", "combate")])
        self.write("viaje.jsonl", [sft("x", "viaje")])
        self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl:1", "repeated", "combate.jsonl:1")

    def test_broken_json_line_names_the_line(self):
        self.write("viaje.jsonl", [sft("v1", "viaje"), "{no json"])
        self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl:2", "not valid JSON")

    def test_only_the_game_split_is_not_an_export(self):
        self.write("train.jsonl", [sft("c1", "combate")])
        self.assertReason(lambda: read_distillation(self.dir), "no <category>.jsonl")

    def test_invalid_utf8_is_a_source_error(self):
        path = os.path.join(self.dir, "viaje.jsonl")
        with open(path, "wb") as fh:
            fh.write(b"\xff\xfe\n")
        self.assertReason(lambda: read_distillation(self.dir), "viaje.jsonl", "not valid UTF-8")

    def test_directories_named_jsonl_are_ignored(self):
        self.write("viaje.jsonl", [sft("a", "viaje")])
        os.mkdir(os.path.join(self.dir, "otra.jsonl"))
        self.assertEqual([e.id for e in read_distillation(self.dir)], ["a"])

    def test_missing_directory(self):
        self.assertReason(lambda: read_distillation(os.path.join(self.dir, "nope")), "directory not found")


class Dpo(Export):
    def test_synthetic_pair_loses_its_marker_and_live_pair_is_marked_live(self):
        path = self.write(
            "live-dpo.jsonl",
            [dpo("a", user="Gorhorn mira al norte.\n\n<!-- scenario-id: viaje-03 -->"), dpo("b")],
        )
        synthetic, live = read_dpo(path)
        self.assertEqual((synthetic.scenario_id, synthetic.origin), ("viaje-03", ORIGIN_SYNTHETIC))
        self.assertEqual(synthetic.prompt[1]["content"], "Gorhorn mira al norte.")
        self.assertEqual((live.scenario_id, live.origin), (None, ORIGIN_LIVE))
        self.assertEqual(live.prompt[1]["content"], "Gorhorn mira al norte.")

    def test_wrong_role_names_the_field(self):
        record = dpo("a")
        record["chosen"][0]["role"] = "user"
        path = self.write("live-dpo.jsonl", [record])
        self.assertReason(lambda: read_dpo(path), "live-dpo.jsonl:1", "chosen[0] must have role 'assistant'")

    def test_chosen_that_is_not_a_narration(self):
        path = self.write("live-dpo.jsonl", [dpo("a", chosen="texto suelto")])
        self.assertReason(lambda: read_dpo(path), "chosen[0].content is not a JSON NarrationResult")

    def test_missing_provider(self):
        record = dpo("a")
        del record["provider"]
        path = self.write("live-dpo.jsonl", [record])
        self.assertReason(lambda: read_dpo(path), "'provider' must be a non-empty string")

    def test_prompt_empty_after_the_mark(self):
        path = self.write("live-dpo.jsonl", [dpo("a", user="\n<!-- scenario-id: viaje-03 -->")])
        self.assertReason(lambda: read_dpo(path), "prompt[1].content is empty after the scenario mark")

    def test_missing_file(self):
        self.assertReason(lambda: read_dpo(os.path.join(self.dir, "x.jsonl")), "DPO export file not found")


class SourceErrorPickle(unittest.TestCase):
    def test_source_error_round_trips(self):
        err = SourceError("a.jsonl", 3, "bad shape")
        err.hint = "kept"
        back = pickle.loads(pickle.dumps(err))
        self.assertEqual((back.path, back.line, back.reason), ("a.jsonl", 3, "bad shape"))
        self.assertEqual(str(back), "a.jsonl:3: bad shape")
        self.assertEqual(back.hint, "kept")  # __dict__ (where add_note keeps notes) survives


if __name__ == "__main__":
    unittest.main()
