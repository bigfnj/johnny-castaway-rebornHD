"""Bind the three bar-removal drafts to the unchanged source-sequence preview."""
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sprites = json.loads((HERE.parent / "tanker-motion-v1/sprites.json").read_text(encoding="utf-8"))

for frame in range(3):
    relative = f"art/cartoon/tanker-v1/generation/TANKER.BMP/{frame:03d}-generated-v2.png"
    source = ROOT / relative
    with Image.open(source) as im:
        box = im.getchannel("A").point(lambda alpha: 255 if alpha >= 8 else 0).getbbox()
        if box is None:
            raise ValueError(f"Empty artwork: {source}")
        sprites[str(frame)]["cartoon"] = dict(
            url=os.path.relpath(source, HERE).replace(os.sep, "/"),
            canvas=list(im.size),
            bounds=list(box),
            path=relative,
            sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        )

(HERE / "sprites.json").write_text(json.dumps(sprites, indent=2) + "\n", encoding="utf-8")
print("Bound 14 original/Cartoon pairs; replaced only Cartoon 000–002; PNG files unchanged")
