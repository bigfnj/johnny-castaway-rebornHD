"""Preserve built-in generation bytes and bind them to their saved request."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    resource, frame, version, raw_path = sys.argv[1:]
    frame = f"{int(frame):03}"
    folder = HERE / "generation" / resource
    request = folder / f"{frame}-v{version}-request.json"
    spec = json.loads(request.read_text(encoding="utf-8"))
    raw = Path(raw_path)
    output = folder / f"{frame}-generated-v{version}.png"
    assert not output.exists(), f"Refusing to overwrite {output}"
    shutil.copyfile(raw, output)
    assert raw.read_bytes() == output.read_bytes()
    with Image.open(output) as im:
        alpha = im.convert("RGBA").getchannel("A")
        stats = {"canvas": list(im.size), "mode": im.mode, "alpha_range": list(alpha.getextrema()),
                 "alpha8_bounds": list(alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()),
                 "edge_alpha_max": max(alpha.crop(b).getextrema()[1] for b in [(0,0,im.width,1),(0,im.height-1,im.width,im.height),(0,0,1,im.height),(im.width-1,0,im.width,im.height)])}
    references = [pin(Path(p)) for p in spec["arguments"]["referenced_image_paths"]]
    record = {"schema_version": 1, "resource": resource, "frame": frame, "version": int(version),
              "tool": "image_gen.imagegen", "mode": "built-in", "request": pin(request), "references": references,
              "raw_tool_output": str(raw), "output": pin(output), "image": stats,
              "postprocessing": "None. Byte-exact copy of the tool result.",
              "appearance_approval": None, "production_integrated": False, "native_motion_checked": False}
    dest = folder / f"{frame}-record-v{version}.json"
    assert not dest.exists()
    dest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))

if __name__ == "__main__":
    main()
