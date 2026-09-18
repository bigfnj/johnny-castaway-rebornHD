"""Record exact raw copies and inputs for the five root-owned drawings."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def ident(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    rows = []
    for name in ("key-output-provenance.json", "raft-output-provenance.json"):
        rows.extend(json.loads((HERE / "generation" / name).read_text(encoding="utf-8")))
    for row in rows:
        folder = HERE / "generation" / row["resource"]
        frame = f'{row["frame"]:03}'
        raw = folder / f"{frame}-generated-v1.png"
        request = folder / f"{frame}-v1-request.json"
        args = json.loads(request.read_text(encoding="utf-8"))
        source = Path(row["generated_source_path"])
        assert raw.read_bytes() == source.read_bytes(), str(raw)
        with Image.open(raw) as im:
            a = im.getchannel("A")
            pixels = {"mode": im.mode, "canvas": list(im.size), "alpha_range": list(a.getextrema()),
                      "alpha_bounds": list(a.getbbox()), "alpha8_bounds": list(a.point(lambda v: 255 if v >= 8 else 0).getbbox())}
        record = {"schema_version": 1, "resource": row["resource"], "frame": frame, "version": 1,
                  "tool": "builtin image_gen", "raw_output": ident(raw), "request": ident(request),
                  "ordered_references": [ident(Path(p)) for p in args["referenced_image_paths"]],
                  "raw_source_path": str(source), "raw_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                  "copied_byte_exact": True, "postprocessing": "None", "pixels": pixels,
                  "approval": None, "production_ready": False}
        (folder / f"{frame}-record-v1.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(f"Recorded {len(rows)} exact raw copies")

if __name__ == "__main__":
    main()
