"""Retain the untouched built-in generation output and its source references."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLDER = HERE / "generation/LILFISH.BMP"
RAW = Path("C:/Users/Admin/.codex/generated_images/01a0a1f0-5ca9-70b3-88cd-a31f4f736e75/exec-33a67e5a-2ab9-4511-bf6b-0d5f7ee4233c.png")
TARGET = FOLDER / "008-generated-v1.png"
shutil.copyfile(RAW, TARGET)
assert RAW.read_bytes() == TARGET.read_bytes()

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

request_path = FOLDER / "008-v1-request.json"
request = json.loads(request_path.read_text(encoding="utf-8"))
refs = [pin(Path(path)) for path in request["referenced_image_paths"]]
with Image.open(TARGET) as im:
    a = im.getchannel("A")
    pixels = {"mode": im.mode, "canvas": list(im.size), "alpha_range": list(a.getextrema()),
              "alpha8_bounds": list(a.point(lambda p: 255 if p >= 8 else 0).getbbox())}
record = {
    "schema_version": 1, "resource": "LILFISH.BMP", "frame": "008", "version": 1,
    "status": "awaiting_human_appearance_review", "tool": "built-in image_gen.imagegen",
    "request": pin(request_path), "output": pin(TARGET), "references": refs,
    "reference_roles": ["Exact original arrangement", "Cartoon fish identity only", "Sunglasses material and fish identity"],
    "original": pin(ROOT / "art/cartoon/gulls-fish-batch-v1/reference/original/LILFISH.BMP/008.png"),
    "feedback": pin(HERE / "feedback.json"), "raw_cache_path": str(RAW),
    "raw_cache_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
    "copied_byte_exact": True, "postprocessing": "None", "pixels": pixels,
    "inspection": "Four heads and four mouths. Left normal fish, lower-left normal fish, lower-right sunglasses fish, upper-right normal fish. Far-right extent is a tail. Bodies overlap with drawn occlusion boundaries; final anatomy remains for human judgment.",
    "approval": None, "native_testing": False, "production_package_changed": False
}
(FOLDER / "008-record-v1.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"saved": pin(TARGET), "pixels": pixels}))
