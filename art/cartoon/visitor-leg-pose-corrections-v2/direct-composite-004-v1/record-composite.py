"""Read-only pixel verification and provenance for the ImageMagick composite."""
import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
ROOT = FAMILY.parents[2]

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

upper = FAMILY / "generation/SSUZY1.BMP/004-generated-v3.png"
lower = FAMILY / "generation/SSUZY1.BMP/003-generated-v2.png"
output = HERE / "004-composite-v1.png"
with Image.open(upper) as im:
    a = np.asarray(im.convert("RGBA")).copy()
with Image.open(lower) as im:
    b = np.asarray(im.convert("RGBA")).copy()
with Image.open(output) as im:
    c = np.asarray(im.convert("RGBA")).copy()
    stats = {"canvas": list(im.size), "mode": im.mode}

checks = []
for label, source, observed, region, destination in [
    ("004 head, face and shoulders", a[:475, :700], c[:475, :700],
     [0, 0, 700, 475], [0, 0, 700, 475]),
    ("004 left upper body, hands and bottle region", a[475:850, :500], c[475:850, :500],
     [0, 475, 500, 850], [0, 475, 500, 850]),
    ("003 intact hip and leg region", b[400:890, 820:1724], c[468:958, 700:1604],
     [820, 400, 1724, 890], [700, 468, 1604, 958]),
]:
    visible = source[:, :, 3] > 0
    different = np.any(source != observed, axis=2) & visible
    count = int(different.sum())
    checks.append({"region": label, "source_box": region, "destination_box": destination,
                   "visible_pixels_checked": int(visible.sum()), "different_pixels": count})
    assert count == 0, f"{output.name}: {label}: {count} source pixels changed"

alpha = c[:, :, 3]
ys, xs = np.where(alpha >= 8)
stats.update(alpha_range=[int(alpha.min()), int(alpha.max())],
             alpha8_bounds=[int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
             edge_alpha_max=int(max(alpha[0].max(), alpha[-1].max(), alpha[:,0].max(), alpha[:,-1].max())))
assert stats["edge_alpha_max"] == 0
record = {
    "schema_version": 1, "resource": "SSUZY1.BMP", "frame": "004", "version": 1,
    "tool": "ImageMagick 7.1.2-24", "mode": "direct-png-composite",
    "method": "Direct source-pixel composite. 004 v3 upper body overlays the intact 003 v2 hips and both legs. Lower source translated (-120,+68) at scale1.0 without rotation. Alpha masks trim only the waist join and old forearm fringe. No image generation, repainting, color changes or limb deformation.",
    "output": pin(output), "references": [pin(upper), pin(lower)],
    "source_roles": ["004 v3: head, upper body, arms, hands and lotion bottle",
                     "003 v2: waist, hips, both legs and both feet"],
    "transforms": {"upper": {"translation": [0,0], "scale": [1,1], "rotation_degrees": 0},
                   "lower": {"translation": [-120,68], "scale": [1,1], "rotation_degrees": 0}},
    "image": stats, "pixel_checks": checks,
    "build_script": pin(HERE / "build-composite.ps1"),
    "masks": [pin(HERE / "upper-mask.png"), pin(HERE / "lower-mask.png")],
    "verification_script": pin(Path(__file__).resolve()),
    "authorization": pin(FAMILY / "feedback-004-direct-composite-v1.json"),
    "appearance_approval": None, "production_integrated": False, "native_motion_checked": False,
}
(HERE / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record))
