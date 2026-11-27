"""0.1.0-5: personal-data filter (invariant 2) and open-teacher filter (invariant 9)."""
import os
import tempfile
import unittest

from gforge.filters import (
    RULE_EMAIL,
    RULE_NAME,
    RULE_PHONE,
    RULE_TEACHER,
    check,
    load_names,
    personal_data,
    screen,
)
from gforge.sources.tarkor import PreferenceExample, SftExample
from gforge.teachers import model_of, teacher_rejection

OPEN = "groq:llama-3.3-70b-versatile"


def sft(id, user="Gorhorn mira al norte.", teacher=OPEN, assistant='{"narration": "Niebla.", "newFacts": []}'):
    return SftExample(id, "viaje", teacher, [
        {"role": "system", "content": "Eres el narrador."},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ])


def pair(id, user="Gorhorn mira al norte.", teacher=OPEN):
    narration = '{"narration": "Niebla.", "newFacts": []}'
    return PreferenceExample(
        id, teacher,
        [{"role": "system", "content": "Eres el narrador."}, {"role": "user", "content": user}],
        [{"role": "assistant", "content": narration}],
        [{"role": "assistant", "content": narration}],
        None,
    )


class PersonalData(unittest.TestCase):
    def test_email_is_rejected_and_the_reason_is_named(self):
        rejection = check(pair("p1", user="Escríbeme a ana.lopez+tarkor@example.org si muero."))
        self.assertEqual(rejection.rule, RULE_EMAIL)
        self.assertIn("prompt[1] contains an e-mail address", rejection.reason)
        self.assertNotIn("example.org", str(rejection))

    def test_phone_is_rejected(self):
        for text in ("Llama al 612 345 678", "mi móvil: +34 612-345-678", "tel 912345678."):
            self.assertEqual(personal_data(text)[0], RULE_PHONE, text)

    def test_short_numbers_are_not_phones(self):
        for text in ("Gana 350 monedas en el año 1247.", "Daño 12-15, vida 80/100.", "Sala 3.2.1"):
            self.assertIsNone(personal_data(text), text)

    def test_real_name_from_the_list_whole_word_any_case(self):
        names = ["Ana López", "Iker"]
        self.assertEqual(personal_data("Saludos de ana  LÓPEZ", names)[0], RULE_NAME)
        self.assertEqual(personal_data("Iker entra.", names)[0], RULE_NAME)
        self.assertIsNone(personal_data("Ikerion entra.", names))
        self.assertIsNone(personal_data("Ana entra.", names))

    def test_assistant_text_is_screened_too(self):
        rejection = check(sft("s1", assistant='{"narration": "Escribe a x@example.org", "newFacts": []}'))
        self.assertEqual(rejection.rule, RULE_EMAIL)
        self.assertIn("messages[2]", rejection.reason)

    def test_load_names_skips_blank_lines_and_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "names.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("# jugadores\nAna López\n\n  Iker  \n")
            self.assertEqual(load_names(path), ["Ana López", "Iker"])


class Teacher(unittest.TestCase):
    def test_closed_teacher_is_rejected_with_the_reason(self):
        for teacher in ("anthropic:claude-sonnet-4", "openai:gpt-4o", "gemini:gemini-2.0-flash", "claude-3-haiku"):
            reason = teacher_rejection(teacher)
            self.assertIsNotNone(reason, teacher)
            self.assertIn("is closed", reason)

    def test_no_teacher_is_rejected(self):
        for teacher in (None, "", "  "):
            self.assertEqual(teacher_rejection(teacher), "no teacher declared")
        self.assertEqual(check(sft("s1", teacher="")).rule, RULE_TEACHER)

    def test_unknown_teacher_fails_closed(self):
        self.assertIn("not on the open-teacher list", teacher_rejection("groq:some-new-model"))

    def test_open_teachers_pass(self):
        for teacher in (OPEN, "cerebras:llama3.1-8b", "cloudflare:@cf/meta/llama-3.3-70b-instruct-fp8-fast",
                        "sambanova:Meta-Llama-3.3-70B-Instruct", "groq:openai/gpt-oss-120b",
                        "sambanova:DeepSeek-R1"):
            self.assertIsNone(teacher_rejection(teacher), teacher)

    def test_model_of(self):
        self.assertEqual(model_of("cloudflare:@cf/meta/Llama-3.3-70b"), "llama-3.3-70b")
        self.assertEqual(model_of("claude-3-haiku"), "claude-3-haiku")

    def test_teacher_is_checked_before_personal_data(self):
        rejection = check(sft("s1", user="a@example.org", teacher="gemini:x"))
        self.assertEqual(rejection.rule, RULE_TEACHER)


class Screen(unittest.TestCase):
    def test_keeps_order_and_examples_whole(self):
        examples = [sft("a"), pair("b", user="mail a@example.org"), sft("c", teacher="openai:gpt-4o"), pair("d")]
        kept, rejections = screen(examples, names=["Ana"])
        self.assertEqual([e.id for e in kept], ["a", "d"])
        self.assertIs(kept[0], examples[0])
        self.assertEqual([(r.id, r.rule) for r in rejections], [("b", RULE_EMAIL), ("c", RULE_TEACHER)])


if __name__ == "__main__":
    unittest.main()
