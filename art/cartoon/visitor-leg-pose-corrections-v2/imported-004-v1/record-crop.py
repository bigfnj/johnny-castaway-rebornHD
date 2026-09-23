"""Record and check the lossless screenshot crop without editing image pixels."""
import hashlib
import json
from pathlib import Path
from PIL import Image

folder = Path(__file__).resolve().parent
root = folder.parents[3]
source = folder / "source-screenshot.png"
output = folder / "004-cropped-v1.png"
def pin(path):
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
with Image.open(source) as src, Image.open(output) as cropped:
    expected = src.convert("RGBA").crop((530, 54, 1020, 358))
    actual = cropped.convert("RGBA")
    assert expected.size == actual.size == (490, 304)
    assert expected.tobytes() == actual.tobytes(), "Crop pixels differ from screenshot"
    alpha = actual.getchannel("A")
    image = {"canvas": list(cropped.size), "mode": cropped.mode,
             "alpha_range": list(alpha.getextrema()), "alpha8_bounds": list(alpha.getbbox()),
             "edge_alpha_max": 255, "background": "Opaque checkerboard baked into supplied screenshot"}
record = {"schema_version": 1, "resource": "SSUZY1.BMP", "frame": "004", "version": 1,
          "tool": "ImageMagick 7.1.2-24", "mode": "direct-screenshot-crop",
          "kind": "imported_screenshot_crop",
          "method": "Exact crop of the supplied screenshot's right-hand drawing. Crop rectangle x=530, y=54, width=490, height=304. No resizing, regeneration or retouching. The screenshot's checkerboard remains baked in.",
          "output": pin(output), "references": [pin(source)],
          "source_roles": ["User-supplied screenshot, right-hand drawing selected for frame 004"],
          "crop": {"x": 530, "y": 54, "width": 490, "height": 304},
          "image": image,
          "pixel_check": {"pixels_compared": 490*304, "different_pixels": 0},
          "command": "magick source-screenshot.png -crop 490x304+530+54 +repage 004-cropped-v1.png",
          "selection_instruction_exact": "can you crop out and use the right image for 004 ?",
          "approval_scope": "User-selected screenshot appearance for 004; native sprite transparency and production integration are not included.",
          "production_integrated": False, "native_motion_checked": False}
(folder / "record.json").write_text(json.dumps(record, indent=2) + chr(10), encoding="utf-8")
print(json.dumps(record, indent=2))

