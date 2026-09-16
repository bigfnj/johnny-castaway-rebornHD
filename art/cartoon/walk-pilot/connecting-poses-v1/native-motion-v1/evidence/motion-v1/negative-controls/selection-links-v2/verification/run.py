import hashlib
from pathlib import Path
import sys
import unittest
import config
import prepare_candidate
import check_selection
config.HERE = config.ROOT / "art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1"
config.OUT = Path(__file__).resolve().parent / "output"
config.OUT.mkdir()
print("WITNESS executed validator SHA256=" + hashlib.sha256(Path(prepare_candidate.__file__).read_bytes()).hexdigest(), flush=True)
def test(self):
    check_selection.main()
suite = unittest.defaultTestLoader.loadTestsFromTestCase(type("SelectionLinks", (unittest.TestCase,), {"test_mixed_version_and_pose_bindings": test}))
raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
