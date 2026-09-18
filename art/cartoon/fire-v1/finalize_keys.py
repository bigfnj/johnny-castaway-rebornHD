"""Record shared key outputs without altering pixels."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN = HERE / "generation"


def ident(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


for item in json.loads((GEN / "key-output-provenance.json").read_text()):
    n, v = item["frame"], item["version"]
    path = GEN / f"{n:03}-generated-v{v}.png"
    request = GEN / f"{n:03}-v{v}-request.json"
    refs = json.loads(request.read_text())["referenced_image_paths"]
    with Image.open(path) as im:
        alpha = im.getchannel("A")
        record = dict(resource="FIRE1.BMP", frame=n, version=v, status="draft_pending_human_review",
                      generated_raw=ident(path), request=ident(request),
                      references=[ident(Path(p)) for p in refs], canvas=list(im.size), mode=im.mode,
                      alpha_range=list(alpha.getextrema()), alpha_bounds=alpha.getbbox(),
                      alpha8_bounds=alpha.point(lambda a: 255 if a >= 8 else 0).getbbox(),
                      generated_source_path=item["generated_source_path"],
                      exact_copy=path.read_bytes() == Path(item["generated_source_path"]).read_bytes(),
                      artistic_pixel_processing=False, engine="builtin_imagegen")
    (GEN / f"{n:03}-record-v{v}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print("Recorded seven shared-key outputs; no pixels changed.")
