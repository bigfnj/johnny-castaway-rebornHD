"""Record unchanged ImageGen outputs for the seven root-authored tanker views."""
import hashlib
import json
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]

def identity(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

for number, version in [(n, 1) for n in range(7)] + [(n, 2) for n in range(3, 7)]:
    frame = f"{number:03}"
    raw = BASE / f"generation/TANKER.BMP/{frame}-generated-v{version}.png"
    request = BASE / f"generation/TANKER.BMP/{frame}-v{version}-request.json"
    data = json.loads(request.read_text(encoding="utf-8"))
    with Image.open(raw) as im:
        alpha = im.getchannel("A")
        raw_record = dict(identity(raw), canvas=list(im.size), mode=im.mode,
                          alpha_range=list(alpha.getextrema()),
                          alpha_bounds=alpha.getbbox(),
                          meaningful_bounds_alpha8=alpha.point(lambda x: 255 if x >= 8 else 0).getbbox())
    record = dict(schema_version=1, status="draft_batch_appearance_review",
                  resource="TANKER.BMP", frame=frame, tool="built-in image_gen",
                  raw=raw_record, request=identity(request),
                  references=[identity(Path(p)) for p in data["referenced_image_paths"]],
                  original=identity(BASE / f"reference/original/TANKER.BMP/{frame}.png"),
                  approval=None, production_package_changed=False,
                  image_processing="Exact copy of returned PNG; no resampling, recoloring or alpha changes.",
                  deferred_work=["Original-canvas uniform fitting and registration", "Yaw and identity continuity in native motion", "Bulk smoke and regressions"])
    (raw.parent / f"{frame}-record-v{version}.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(frame, version, raw_record["canvas"], raw_record["alpha_range"])
