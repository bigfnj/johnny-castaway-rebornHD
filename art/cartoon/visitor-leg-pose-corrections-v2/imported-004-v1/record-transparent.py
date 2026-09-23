"""Read-only pixel and alpha verification for the cropped screenshot cutout."""
import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np

folder = Path(__file__).resolve().parent
root = folder.parents[3]
def pin(path):
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
output = folder / "004-transparent-v1.png"
with Image.open(output) as im, Image.open(folder / "004-cropped-v1.png") as src:
    a = np.array(im.convert("RGBA"))
    b = np.array(src.convert("RGBA"))
    visible = a[:,:,3] > 0
    assert a.shape == b.shape == (304,490,4)
    differences = int(np.any(a[:,:,:3] != b[:,:,:3], axis=2)[visible].sum())
    assert differences == 0
    alpha = im.getchannel("A")
    edge_max = int(max(a[0,:,3].max(), a[-1,:,3].max(), a[:,0,3].max(), a[:,-1,3].max()))
    assert edge_max == 0
    assert alpha.getextrema() == (0,255)
    image = {"canvas": list(im.size), "mode": im.mode,
             "alpha_range": list(alpha.getextrema()), "alpha8_bounds": list(alpha.getbbox()),
             "edge_alpha_max": edge_max, "background": "Transparent"}
record = {"schema_version": 1, "resource": "SSUZY1.BMP", "frame": "004", "version": 1,
          "tool": "ImageMagick 7.1.2-24", "mode": "direct-screenshot-cutout",
          "kind": "imported_screenshot_cutout",
          "method": "Right-hand drawing cropped from the user screenshot, then the connected pale checkerboard background removed into an alpha mask. No generation, resizing or repainting. All retained drawing RGB pixels are unchanged.",
          "output": pin(output),
          "references": [pin(folder / "source-screenshot.png"), pin(folder / "004-cropped-v1.png")],
          "crop_record": pin(folder / "record.json"),
          "processing_script": pin(folder / "remove-checkerboard.ps1"),
          "alpha_mask": pin(folder / "foreground-alpha.png"),
          "image": image,
          "pixel_check": {"retained_pixels": int(visible.sum()), "different_retained_rgb_pixels": differences,
                          "transparent_pixels": int((~visible).sum())},
          "selection_instruction_exact": "can you crop out and use the right image for 004 ?",
          "followup_instruction_exact": "certainly we dont need the checkerboard, but you are able to use the image?",
          "approval_scope": "User-selected screenshot drawing for 004, with checkerboard removed as requested.",
          "production_integrated": False, "native_motion_checked": False}
(folder / "transparent-record.json").write_text(json.dumps(record, indent=2) + chr(10), encoding="utf-8")
print(json.dumps(record, indent=2))

