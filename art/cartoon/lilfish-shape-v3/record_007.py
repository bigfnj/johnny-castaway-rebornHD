"""Copy a built-in output unchanged and bind this four-fish appearance variant."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
version, raw = int(sys.argv[1]), Path(sys.argv[2])
folder = HERE / "generation/LILFISH.BMP"
output = folder / f"007-generated-v{version}.png"
shutil.copyfile(raw, output)
assert raw.read_bytes() == output.read_bytes()
def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
request_path = folder / f"007-v{version}-request.json"
request = json.loads(request_path.read_text(encoding="utf-8"))
refs = []
for value in request["referenced_image_paths"]:
    path = Path(value)
    refs.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
with Image.open(output) as im:
    a = im.getchannel("A")
    pixels = {"mode": im.mode, "canvas": list(im.size), "alpha_range": list(a.getextrema()),
              "alpha8_bounds": list(a.point(lambda p: 255 if p >= 8 else 0).getbbox())}
record = {"schema_version": 1, "resource": "LILFISH.BMP", "frame": "007", "version": version,
          "tool": "built-in image_gen.imagegen", "status": "awaiting_appearance_review" if version > 1 else "earlier_attempt_sunglasses_fish_angle_drifted",
          "request": pin(request_path), "output": pin(output), "references": refs, "feedback": pin(HERE / "feedback.json"),
          "raw_cache_path": str(raw), "raw_cache_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
          "copied_byte_exact": True, "postprocessing": "None", "pixels": pixels,
          "art_direction": "User-directed four-fish alternative for original007, whose original and native catch script contain three fish. Native count is unchanged.",
          "inspection": "Four independent compact fish visible. Only the lower-right fish wears sunglasses. " + ("This earlier attempt turned the sunglasses fish left and is not selected." if version == 1 else "The sunglasses fish faces down-right; the other three retain compact separate bodies."),
          "approval": None, "native_testing": False, "production_package_changed": False}
(folder / f"007-record-v{version}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"saved": pin(output), "pixels": pixels}))
