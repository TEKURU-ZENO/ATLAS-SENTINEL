import sys
import unittest
from pathlib import Path


BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT / "packages" / "safety-rules"))
sys.path.insert(0, str(ROOT / "apps" / "simulator"))

suite = unittest.defaultTestLoader.discover(str(BACKEND / "tests"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
