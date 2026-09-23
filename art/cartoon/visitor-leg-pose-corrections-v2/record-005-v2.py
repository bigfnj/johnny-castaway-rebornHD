"""Read-only image inspection and provenance for the built-in 005 v2 output."""
import hashlib
import json
from pathlib import Path
from PIL import Image

family = Path(__file__).resolve().parent
root = family.parents[2]
generation = family / "generation/SSUZY1.BMP"
request_path = generation / "005-v2-request.json"
output_path = generation / "005-generated-v2.png"
raw_path = Path("C:/Users/Admin/.codex/generated_images/01a0a1f0-5ca9-70b3-88cd-a31f4f736e75/exec-f8a4286e-7072-485b-8de1-2173e7809d4d.png")
def pin(path):
    path = Path(path)
    return {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
request = json.loads(request_path.read_text(encoding="utf-8-sig"))
with Image.open(output_path) as im:
    mode = im.mode
    canvas = list(im.size)
    alpha = im.convert("RGBA").getchannel("A")
    bounds = alpha.point(lambda p: 255 if p > 8 else 0).getbbox()
    width, height = im.size
    edge_alpha_max = max(alpha.crop(box).getextrema()[1] for box in [
        (0, 0, width, 1), (0, height-1, width, height),
        (0, 0, 1, height), (width-1, 0, width, height)])
    stats = {"canvas": canvas, "mode": mode, "alpha_range": list(alpha.getextrema()),
             "alpha8_bounds": list(bounds) if bounds else None,
             "edge_alpha_max": edge_alpha_max}
assert output_path.read_bytes() == raw_path.read_bytes()
record = {"schema_version": 1, "resource": "SSUZY1.BMP", "frame": "005", "version": 2,
          "tool": "image_gen.imagegen", "mode": "built-in", "request": pin(request_path),
          "references": [pin(p) for p in request["arguments"]["referenced_image_paths"]],
          "raw_tool_output": str(raw_path), "output": pin(output_path), "image": stats,
          "postprocessing": "None. Byte-exact copy of the tool result.",
          "appearance_approval": None, "production_integrated": False, "native_motion_checked": False}
record_path = generation / "005-record-v2.json"
record_path.write_text(json.dumps(record, indent=2) + chr(10), encoding="utf-8")
print(json.dumps(record, indent=2))

