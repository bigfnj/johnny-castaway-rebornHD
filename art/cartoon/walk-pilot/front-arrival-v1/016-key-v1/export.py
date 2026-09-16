"""Export only front wait 016 at the reviewed walking family's fixed scale.

Prepare a recipe with --prepare --source BASENAME.png, or reproduce with
--recipe PATH. --preview-only retains overhang in padding and writes no runtime
sprite. This technical export does not assign artistic or motion approval.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
FRAME = 16
SCALE = .1
PAD = 64
TARGET = [35, .25]
FILTERS = {"working_mode": "RGBa", "affine": "BICUBIC", "oversample": 8,
           "downsample": "LANCZOS", "output_mode": "RGBA", "png_compress_level": 9}
REFERENCE_HASHES = {
    "source.json": "08501f2e05651f7e818e7ce6f274e564b7c84b1a39f4a9211396559715d70125",
    "016-original-native.png": "7968a4d2f2a4c8279f07c40f50ce918ca4691379e48cb0b4901b3d6fcaa1fa2b",
    "016-original-nearest8.png": "17d68191c85315e1759edf357920d2642f791ce6a5dd5cf1871899c2b0854d92",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def png(image):
    output = io.BytesIO()
    image.save(output, format="PNG", compress_level=9)
    return output.getvalue()


def reference():
    for name, expected in REFERENCE_HASHES.items():
        require(sha((HERE / "reference" / name).read_bytes()) == expected,
                "reference-file:" + name)
    return json.loads((HERE / "reference/source.json").read_bytes())["original_frame"]


def source_bytes(name):
    require(isinstance(name, str) and name not in ("", ".", "..") and
            "/" not in name and "\\" not in name and ":" not in name and
            Path(name).suffix.lower() == ".png", "source-path:016")
    return (HERE / name).read_bytes()


def measure_cap(image):
    alpha = image.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
    require(bounds is not None and bounds[1] < 300, "cap-outline:016")
    y = bounds[1]
    xs = [x for x in range(image.width) if alpha.getpixel((x, y)) >= 128]
    return [(min(xs) + max(xs) + 1) / 2, y]


def prepare(name):
    original = reference()
    data = source_bytes(name)
    with Image.open(io.BytesIO(data)) as image:
        require(image.mode == "RGBA" and image.size == (1024, 1536), "prepare-canvas:016")
        cap = measure_cap(image)
    tx, ty = TARGET[0] - cap[0] * SCALE, TARGET[1] - cap[1] * SCALE
    return {
        "schema_version": 1,
        "scope": "Technical front-wait-016 review only; no runtime or motion approval.",
        "reference_hashes": REFERENCE_HASHES.copy(),
        "reference_limit": "Stored original references checked; commercial RESOURCE inputs are not reread.",
        "scale_exact": {"numerator": 1, "denominator": 10},
        "normalization": "none", "padding_hd": PAD, "resampling": FILTERS.copy(),
        "pillow_version": PIL.__version__, "cap_target_hd": TARGET.copy(),
        "cap_measurement": "First alpha>=128 row; its pixel-edge horizontal midpoint and row top. Outline observation, not an anatomical landmark.",
        "target_basis": "Original016 row0 span x[15,20) has midpoint17.5, doubled to35HD; y0.25 is the inherited deliberate filter margin.",
        "frames": [{"frame": FRAME, "source": name, "source_sha256": sha(data),
                    "generated_canvas": [1024, 1536],
                    "runtime_canvas": [n * 2 for n in original["canvas"]],
                    "cap_raw": cap, "cap_target_hd": TARGET.copy(),
                    "affine_forward": [SCALE, 0, tx, 0, SCALE, ty]}],
    }


def render(recipe, preview_only=False):
    original = reference()
    require(recipe["reference_hashes"] == REFERENCE_HASHES, "recipe-reference:016")
    require(recipe["schema_version"] == 1 and
            recipe["scale_exact"] == {"numerator": 1, "denominator": 10} and
            recipe["normalization"] == "none" and recipe["padding_hd"] == PAD and
            recipe["resampling"] == FILTERS and recipe["pillow_version"] == PIL.__version__,
            "render-contract:016")
    require([item["frame"] for item in recipe["frames"]] == [FRAME], "only-arrival:016")
    item = recipe["frames"][0]
    data = source_bytes(item["source"])
    require(sha(data) == item["source_sha256"], "source-identity:016")
    with Image.open(io.BytesIO(data)) as source:
        require(source.mode == "RGBA" and source.size == (1024, 1536) and
                item["generated_canvas"] == [1024, 1536], "source-canvas:016")
        cap = measure_cap(source)
        tx, ty = TARGET[0] - cap[0] * SCALE, TARGET[1] - cap[1] * SCALE
        expected = [SCALE, 0, tx, 0, SCALE, ty]
        require(item["cap_raw"] == cap and item["cap_target_hd"] == TARGET and
                recipe["cap_target_hd"] == TARGET and len(item["affine_forward"]) == 6 and
                all(math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
                    for a, b in zip(item["affine_forward"], expected)), "fixed-registration:016")
        canvas = [n * 2 for n in original["canvas"]]
        require(item["runtime_canvas"] == canvas, "runtime-canvas:016")
        width, height = canvas
        bounds = source.getchannel("A").point(lambda v: 255 if v >= 8 else 0).getbbox()
        centers = [(bounds[0] + .5) * SCALE + tx, (bounds[1] + .5) * SCALE + ty,
                   (bounds[2] - .5) * SCALE + tx, (bounds[3] - .5) * SCALE + ty]
        fits = centers[0] >= 0 and centers[1] >= 0 and centers[2] < width and centers[3] < height
        require(preview_only or fits, "runtime-overhang:016")
        size = (width + PAD * 2, height + PAD * 2)
        high = source.convert("RGBa").transform((size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
            (1 / (SCALE * 8), 0, -(tx + PAD) / SCALE,
             0, 1 / (SCALE * 8), -(ty + PAD) / SCALE),
            resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        padded = high.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
        filtered = padded.getchannel("A").point(lambda v: 255 if v >= 8 else 0).getbbox()
        fixed = padded.crop((PAD, PAD, PAD + width, PAD + height))
        images = {"padded/016.png": png(padded)}
        if not preview_only:
            images["BMP/JOHNWALK.BMP/016.png"] = png(fixed)
    report = {
        "schema_version": 1, "scope": "Technical export only; not native capture or human acceptance.",
        "preview_only": preview_only, "runtime_sprites_written": not preview_only,
        "runtime_fit_all_source_centers": fits, "scale": SCALE, "padding_hd": PAD,
        "reference_hashes": REFERENCE_HASHES.copy(),
        "reference_limit": "Stored original references checked; commercial RESOURCE inputs are not reread.",
        "frames": [{"frame": FRAME, "source": item["source"], "source_sha256": sha(data),
                    "cap_raw": cap, "runtime_canvas": canvas, "affine_forward": expected,
                    "alpha8_source_bounds": list(bounds), "alpha8_centers_hd": centers,
                    "source_centers_fit_runtime": fits,
                    "filtered_alpha8_bounds_hd_exclusive": [filtered[0] - PAD, filtered[1] - PAD,
                                                            filtered[2] - PAD, filtered[3] - PAD],
                    "padded_canvas": list(size)}],
        "outputs_sha256": {name: sha(value) for name, value in images.items()},
        "filter_limit": "Source-center fit does not promise absence of low-alpha filter fringe; padded output retains it.",
    }
    return images, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--source", help="Explicit PNG basename in this authoring folder; requires --prepare")
    parser.add_argument("--recipe", type=Path, help="Explicit saved recipe for reproduction")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    print("WITNESS export.py SHA256=" + sha(Path(__file__).read_bytes()), flush=True)
    try:
        require((args.prepare and args.source is not None and args.recipe is None) or
                (not args.prepare and args.source is None and args.recipe is not None),
                "explicit-input:016")
        require(not args.output.exists(), "output-already-exists")
        if args.prepare:
            recipe = prepare(args.source)
            recipe_bytes = (json.dumps(recipe, indent=2) + "\n").encode("utf-8")
        else:
            recipe_bytes = args.recipe.read_bytes()
            recipe = json.loads(recipe_bytes)
        images, report = render(recipe, args.preview_only)
        report["recipe_sha256"] = sha(recipe_bytes)
        report["export_source_sha256"] = sha(Path(__file__).read_bytes())
        args.output.mkdir(parents=True, exist_ok=False)
        for name, data in images.items():
            destination = args.output / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        (args.output / "recipe.json").write_bytes(recipe_bytes)
        (args.output / "export-report.json").write_text(json.dumps(report, indent=2) + "\n",
                                                       encoding="utf-8", newline="\n")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS front-wait016; " + ("PREVIEW ONLY: runtime sprite not written" if args.preview_only
                                  else "runtime-canvas candidate written; not promoted"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
