"""The core must parse as Python 3.8."""
import ast
import glob
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Py38Syntax(unittest.TestCase):
    def test_gforge_parses_as_py38(self):
        files = glob.glob(os.path.join(ROOT, "gforge", "**", "*.py"), recursive=True)
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path):
                with open(path, encoding="utf-8") as fh:
                    ast.parse(fh.read(), filename=path, feature_version=(3, 8))


if __name__ == "__main__":
    unittest.main()
