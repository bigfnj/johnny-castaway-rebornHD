#!/usr/bin/env python3
"""Reproduce six pending-review candidate sprites in a new output directory."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
CANVASES = {24: [64, 150], 25: [80, 148], 26: [80, 146], 27: [64, 144], 28: [64, 144], 29: [64, 150]}
CAPS = {frame: ([388, 40] if frame == 28 else [385, 42]) for frame in CANVASES}
TARGETS = {24: [17.5, .25], 25: [23.5, .25], 26: [25.5, .25], 27: [17.5, .25], 28: [17.5, .25], 29: [17.5, .25]}
RESAMPLING = {"pillow_version": "12.3.0", "working_mode": "RGBa", "affine_filter": "BICUBIC", "oversample": 8, "downsample_filter": "LANCZOS", "output_mode": "RGBA", "png_compress_level": 9}
digest = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory; existing outputs are never overwritten")
    args = parser.parse_args()
    output = args.output.resolve()
    recipe = json.loads((HERE / "recipe.json").read_text(encoding="utf-8"))
    if output.exists():
        parser.error("refusing existing output: " + str(output))
    if PIL.__version__ != "12.3.0":
        parser.error("Pillow12.3.0 is required for these exact PNG bytes; found " + PIL.__version__)
    if recipe["scale_exact"] != {"numerator": 1, "denominator": 10} or recipe["normalization"] != "none":
        parser.error("recipe.json: requires scale1/10 and no normalization")
    if recipe["resampling"] != RESAMPLING:
        parser.error("recipe.json: resampling contract differs")
    expected_paths = [f"BMP/JOHNWALK.BMP/{frame:03}.png" for frame in CANVASES]
    if recipe["required_assets"] != expected_paths or [item["path"] for item in recipe["frames"]] != expected_paths or [item["frame"] for item in recipe["frames"]] != list(CANVASES):
        parser.error("recipe.json: expected exactly ordered024-029 frame paths")
    bundle = HERE / "source-images.zip"
    if recipe["source_bundle"]["file"] != bundle.name or digest(bundle.read_bytes()) != recipe["source_bundle"]["sha256"] or bundle.stat().st_size != recipe["source_bundle"]["bytes"]:
        parser.error("source-images.zip: source bundle identity mismatch")
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(recipe["generated_images"]) or sorted(names) != recipe["source_bundle"]["members"]:
            parser.error("source-images.zip: missing, unexpected or duplicate member")
        sources = {name: archive.read(name) for name in names}
    for name, raw in sources.items():
        if digest(raw) != recipe["generated_images"][name]["sha256"]:
            parser.error(name + ": generated source identity mismatch")
    rendered = []
    for item in recipe["frames"]:
        frame, path, name = item["frame"], item["path"], item["generated_image"]
        raw = sources[name]
        with Image.open(io.BytesIO(raw)) as source:
            if source.mode != "RGBA" or list(source.size) != item["generated_canvas"] or item["generated_canvas"] != [1024, 1536] or recipe["generated_images"][name]["canvas"] != item["generated_canvas"]:
                parser.error(name + ": expected RGBA1024x1536 source canvas")
            if digest(raw) != item["source_sha256"]:
                parser.error(name + ": frame source identity mismatch")
            scale, xy, tx, yx, sy, ty = item["affine_forward"]
            if scale != .1 or sy != .1 or xy != 0 or yx != 0:
                parser.error(path + ": requires the common uniform scale0.1")
            cap, target = item["cap_raw"], item["cap_target_hd"]
            if cap != CAPS[frame] or target != TARGETS[frame] or not all(math.isclose(a, b, rel_tol=0, abs_tol=1e-12) for a, b in zip((cap[0]*scale+tx, cap[1]*scale+ty), target)):
                parser.error(path + ": cap registration differs from recipe")
            if item["runtime_canvas"] != CANVASES[frame]:
                parser.error(path + ": runtime canvas differs from recorded frame")
            width, height = item["runtime_canvas"]
            bounds = source.getchannel("A").point(lambda value: 255 if value >= 8 else 0).getbbox()
            if bounds is None or (bounds[0]+.5)*scale+tx < 0 or (bounds[2]-.5)*scale+tx >= width or (bounds[1]+.5)*sy+ty < 0 or (bounds[3]-.5)*sy+ty >= height:
                parser.error(path + ": alpha8 source centers outside runtime canvas")
            high = source.convert("RGBa").transform((width*8, height*8), Image.Transform.AFFINE, (1/(scale*8), 0, -tx/scale, 0, 1/(scale*8), -ty/scale), resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
            image = high.resize((width, height), Image.Resampling.LANCZOS).convert("RGBA")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", compress_level=9)
            data = buffer.getvalue()
            if digest(data) != item["candidate_png_sha256"] or len(data) != item["candidate_png_bytes"]:
                parser.error(path + ": exported PNG differs from recorded candidate")
            rendered.append((path, data))
    # All source, recipe and rendered-byte checks precede directory creation.
    output.mkdir(parents=True, exist_ok=False)
    for name, data in rendered:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({"status": "six recorded candidate PNG hashes matched", "frames": len(rendered), "coverage": "partial", "human_motion_acceptance": False, "production_acceptance": False, "output": str(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
