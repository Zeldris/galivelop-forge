"""Prueba mínima para que el check tenga algo que ejecutar hasta que exista el paquete gforge (F1)."""
import unittest


class Smoke(unittest.TestCase):
    def test_python_version(self):
        import sys
        self.assertGreaterEqual(sys.version_info[:2], (3, 8))


if __name__ == "__main__":
    unittest.main()
