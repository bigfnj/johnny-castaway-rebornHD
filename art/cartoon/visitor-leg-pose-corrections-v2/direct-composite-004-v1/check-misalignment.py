"""Exercise the pixel comparison with a one-pixel bad registration in memory."""
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
script = here / "record-composite.py"
record = here / "record.json"
before = hashlib.sha256(record.read_bytes()).hexdigest()
source = script.read_text(encoding="utf-8")
old = "c[468:958, 700:1604]"
assert source.count(old) == 1
mutated = source.replace(old, "c[468:958, 701:1605]")
try:
    exec(compile(mutated, str(script), "exec"),
         {"__file__": str(script), "__name__": "__main__"})
except AssertionError as exc:
    failure = str(exc)
    assert failure.startswith("004-composite-v1.png: 003 intact hip and leg region:")
else:
    raise AssertionError("Misaligned region was not rejected")
assert hashlib.sha256(record.read_bytes()).hexdigest() == before
result = {"mutation": "Shift the observed donor region right by one pixel in memory",
          "expected_failures": 1, "observed_failures": 1, "failure": failure,
          "actual_image_files_changed": False, "record_unchanged": True}
(here / "verification-mutation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
