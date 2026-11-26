"""Invariant 7: the core imports with the stdlib only."""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAVY = ("unsloth", "torch", "transformers", "huggingface_hub", "numpy")


def run(code):
    return subprocess.run(
        [sys.executable, "-S", "-c", code],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


class CleanImport(unittest.TestCase):
    def test_import_loads_no_heavy_module(self):
        code = (
            "import sys; sys.path.insert(0, %r); import gforge; "
            "print(repr([m for m in %r if m in sys.modules]))" % (ROOT, HEAVY)
        )
        proc = run(code)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "[]")

    def test_train_without_trainer_names_the_extra(self):
        code = (
            "import sys; sys.path.insert(0, %r); import gforge\n"
            "try:\n    gforge.train({})\n"
            "except gforge.PortUnavailable as e:\n    print(e)\n" % ROOT
        )
        proc = run(code)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("galivelop-forge[unsloth]", proc.stdout)


if __name__ == "__main__":
    unittest.main()
