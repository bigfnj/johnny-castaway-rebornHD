"""Build an isolated source-sequence comparison; do not alter artwork or runtime."""
import hashlib
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
selection = json.loads((HERE.parent / "ships-batch-v1/review-record.json").read_text(encoding="utf-8"))
sprites = {}
for asset in selection["assets"]:
    if asset["resource"] != "TANKER.BMP":
        continue
    frame = int(asset["frame"])
    item = {}
    for role, key in [("original", "original_reference"), ("cartoon", "selected_raw")]:
        source = ROOT / asset[key]["path"]
        with Image.open(source) as im:
            alpha = im.getchannel("A")
            box = alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()
            item[role] = dict(url=os.path.relpath(source, HERE).replace(os.sep, "/"),
                              canvas=list(im.size), bounds=list(box),
                              path=asset[key]["path"], sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    sprites[frame] = item
(HERE / "sprites.json").write_text(json.dumps(sprites, indent=2)+"\n", encoding="utf-8")
print(f"Bound {len(sprites)} original/Cartoon sprite pairs; PNG files unchanged")
