#!/usr/bin/env python3
"""Recreate six review-candidate PNGs from durable sources and registrations."""
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
REPO = HERE.parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory for six recorded review-candidate PNGs")
    args = parser.parse_args()
    recipe = json.loads((HERE / "recipe.json").read_text(encoding="utf-8"))
    expected_version = recipe["resampling"]["pillow_version"]
    if PIL.__version__ != expected_version:
        parser.error(f"recorded byte-exact export requires Pillow {expected_version}; found {PIL.__version__}")
    output = args.output.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing output: {output}")
    bundle = HERE / recipe["source_bundle"]["file"]
    if digest(bundle.read_bytes()) != recipe["source_bundle"]["sha256"]:
        parser.error("source-images.zip: source bundle hash mismatch")
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(recipe["generated_images"]):
            parser.error("source-images.zip: unexpected or duplicate entries")
        sources = {name: archive.read(name) for name in names}
    for name, data in sources.items():
        if digest(data) != recipe["generated_images"][name]["sha256"]:
            parser.error(f"{name}: generated source hash mismatch")
    canonical = recipe["canonical_character"]
    if digest((REPO / canonical["file"]).read_bytes()) != canonical["sha256"]:
        parser.error("canonical character reference hash mismatch")
    with zipfile.ZipFile(REPO / recipe["original_archive"]["file"]) as archive:
        for reference in recipe["original_references"].values():
            if digest(archive.read(reference["member"])) != reference["sha256"]:
                parser.error(f"{reference['member']}: original pose reference hash mismatch")

    # Compute and check every image before creating the output directory.
    rendered = []
    for frame in recipe["frames"]:
        source = Image.open(io.BytesIO(sources[frame["generated_image"]])).convert("RGBA")
        if list(source.size) != frame["generated_canvas"]:
            parser.error(f"{frame['path']}: source dimensions differ from recipe")
        common = frame["drawing_export_scale_exact"]
        normalization = frame["canvas_normalization"]["uniform_factor_exact"]
        nominal = (common["numerator"] / common["denominator"] *
                   normalization["numerator"] / normalization["denominator"])
        scale, xy, tx, yx, scale_y, ty = frame["affine_forward"]
        if xy != 0 or yx != 0 or scale != scale_y or not math.isclose(scale, nominal, rel_tol=1e-14):
            parser.error(f"{frame['path']}: transform is not the declared uniform scale")
        cap, target = frame["cap_generated"], frame["cap_target_hd"]
        if not all(math.isclose(value, expected, abs_tol=1e-12)
                   for value, expected in zip((cap[0]*scale+tx, cap[1]*scale+ty), target)):
            parser.error(f"{frame['path']}: cap registration differs from recipe")
        width, height = frame["runtime_canvas"]
        high = source.convert("RGBa").transform(
            (width*8, height*8), Image.Transform.AFFINE,
            (1/(scale*8), 0, -tx/scale, 0, 1/(scale*8), -ty/scale),
            resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        image = high.resize((width, height), Image.Resampling.LANCZOS).convert("RGBA")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", compress_level=9)
        data = buffer.getvalue()
        if digest(data) != frame["candidate_png_sha256"]:
            parser.error(f"{frame['path']}: export differs from recorded candidate PNG bytes")
        rendered.append((frame["path"], data))
    for name, data in rendered:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({"status": "all recorded candidate PNG hashes matched", "frames": len(rendered),
                      "output": str(output), "coverage": "partial"}, sort_keys=True))


if __name__ == "__main__":
    main()
