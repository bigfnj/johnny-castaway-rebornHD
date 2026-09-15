"""Export one selected remaining wait pose (000 or 015) at fixed family scale.

Prepare with --frame N --prepare --source BASENAME.png, or reproduce with
--frame N --recipe PATH. --preview-only retains overhang in padding and writes no runtime
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
SCALE = .1
PAD = 64
TARGETS = {0: [54, .25], 15: [35, .25]}
FILTERS = {"working_mode": "RGBa", "affine": "BICUBIC", "oversample": 8,
           "downsample": "LANCZOS", "output_mode": "RGBA", "png_compress_level": 9}
REFERENCE_HASHES = {
    0: {
        "000-source.json": "42233146f463bad1c8fdfe7c135bc35e518f06ac6bf77012f38a7f754042cf2b",
        "000-original-native.png": "e671e0c24432a633450d7e64e5e5f8aa54f7b31ca9e2381ecbd6b15ff130be52",
        "000-original-nearest8.png": "b61aeae2496fc2a169bbdb8ca1254802499a59a5ea282894773f865e64ffc321",
    },
    15: {
        "015-source.json": "48a2b5329b1a446babc6421f3a13843b500537063ae42c5826e6df439ac459f4",
        "015-original-native.png": "0ec7a74ec974aa38fef751f22d7f9c42f198a8e5d1bff711bbed1f6bb7414b66",
        "015-original-nearest8.png": "afba9900490c794c0260081208278b197758bd95360df3e4374eb227c09621e0",
    },
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


def check_frame(frame):
    require(type(frame) is int and frame in (0, 15), "allowed-frame")


def reference(frame):
    check_frame(frame)
    for name, expected in REFERENCE_HASHES[frame].items():
        require(sha((HERE / "reference" / name).read_bytes()) == expected,
                "reference-file:" + name)
    return json.loads((HERE / "reference" / f"{frame:03}-source.json").read_bytes())["original_frame"]


def source_bytes(name, frame):
    require(isinstance(name, str) and name not in ("", ".", "..") and
            "/" not in name and "\\" not in name and ":" not in name and
            Path(name).suffix.lower() == ".png", f"source-path:{frame:03}")
    return (HERE / name).read_bytes()


def measure_cap(image, frame):
    alpha = image.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
    require(bounds is not None and bounds[1] < 300, f"cap-outline:{frame:03}")
    y = bounds[1]
    xs = [x for x in range(image.width) if alpha.getpixel((x, y)) >= 128]
    return [(min(xs) + max(xs) + 1) / 2, y]


def prepare(frame, name):
    original = reference(frame)
    target, hashes = TARGETS[frame], REFERENCE_HASHES[frame]
    data = source_bytes(name, frame)
    with Image.open(io.BytesIO(data)) as image:
        require(image.mode == "RGBA" and image.size == (1024, 1536), f"prepare-canvas:{frame:03}")
        cap = measure_cap(image, frame)
    tx, ty = target[0] - cap[0] * SCALE, target[1] - cap[1] * SCALE
    return {
        "schema_version": 1,
        "scope": f"Technical remaining-wait-{frame:03} review only; no runtime or motion approval.",
        "reference_hashes": hashes.copy(),
        "reference_limit": "Stored original references checked; commercial RESOURCE inputs are not reread.",
        "scale_exact": {"numerator": 1, "denominator": 10},
        "normalization": "none", "padding_hd": PAD, "resampling": FILTERS.copy(),
        "pillow_version": PIL.__version__, "cap_target_hd": target.copy(),
        "cap_measurement": "First alpha>=128 row; its pixel-edge horizontal midpoint and row top. Outline observation, not an anatomical landmark.",
        "target_basis": f"Original{frame:03} top-row pixel-edge midpoint doubled to{target[0]}HD; y0.25 is the inherited deliberate filter margin.",
        "frames": [{"frame": frame, "source": name, "source_sha256": sha(data),
                    "generated_canvas": [1024, 1536],
                    "runtime_canvas": [n * 2 for n in original["canvas"]],
                    "cap_raw": cap, "cap_target_hd": target.copy(),
                    "affine_forward": [SCALE, 0, tx, 0, SCALE, ty]}],
    }


def render(recipe, frame, preview_only=False):
    check_frame(frame)
    require(isinstance(recipe["frames"], list) and len(recipe["frames"]) == 1 and
            type(recipe["frames"][0]["frame"]) is int and recipe["frames"][0]["frame"] == frame,
            f"recipe-frame:{frame:03}")
    original = reference(frame)
    target, hashes = TARGETS[frame], REFERENCE_HASHES[frame]
    require(recipe["reference_hashes"] == hashes, f"recipe-reference:{frame:03}")
    require(recipe["schema_version"] == 1 and
            recipe["scale_exact"] == {"numerator": 1, "denominator": 10} and
            recipe["normalization"] == "none" and recipe["padding_hd"] == PAD and
            recipe["resampling"] == FILTERS and recipe["pillow_version"] == PIL.__version__,
            f"render-contract:{frame:03}")
    item = recipe["frames"][0]
    data = source_bytes(item["source"], frame)
    require(sha(data) == item["source_sha256"], f"source-identity:{frame:03}")
    with Image.open(io.BytesIO(data)) as source:
        require(source.mode == "RGBA" and source.size == (1024, 1536) and
                item["generated_canvas"] == [1024, 1536], f"source-canvas:{frame:03}")
        cap = measure_cap(source, frame)
        tx, ty = target[0] - cap[0] * SCALE, target[1] - cap[1] * SCALE
        expected = [SCALE, 0, tx, 0, SCALE, ty]
        require(item["cap_raw"] == cap and item["cap_target_hd"] == target and
                recipe["cap_target_hd"] == target and len(item["affine_forward"]) == 6 and
                all(math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
                    for a, b in zip(item["affine_forward"], expected)), f"fixed-registration:{frame:03}")
        canvas = [n * 2 for n in original["canvas"]]
        require(item["runtime_canvas"] == canvas, f"runtime-canvas:{frame:03}")
        width, height = canvas
        bounds = source.getchannel("A").point(lambda v: 255 if v >= 8 else 0).getbbox()
        centers = [(bounds[0] + .5) * SCALE + tx, (bounds[1] + .5) * SCALE + ty,
                   (bounds[2] - .5) * SCALE + tx, (bounds[3] - .5) * SCALE + ty]
        fits = centers[0] >= 0 and centers[1] >= 0 and centers[2] < width and centers[3] < height
        require(preview_only or fits, f"runtime-overhang:{frame:03}")
        size = (width + PAD * 2, height + PAD * 2)
        high = source.convert("RGBa").transform((size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
            (1 / (SCALE * 8), 0, -(tx + PAD) / SCALE,
             0, 1 / (SCALE * 8), -(ty + PAD) / SCALE),
            resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        padded = high.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
        filtered = padded.getchannel("A").point(lambda v: 255 if v >= 8 else 0).getbbox()
        fixed = padded.crop((PAD, PAD, PAD + width, PAD + height))
        images = {f"padded/{frame:03}.png": png(padded)}
        if not preview_only:
            images[f"BMP/JOHNWALK.BMP/{frame:03}.png"] = png(fixed)
    report = {
        "schema_version": 1, "scope": "Technical export only; not native capture or human acceptance.",
        "preview_only": preview_only, "runtime_sprites_written": not preview_only,
        "runtime_fit_all_source_centers": fits, "scale": SCALE, "padding_hd": PAD,
        "reference_hashes": hashes.copy(),
        "reference_limit": "Stored original references checked; commercial RESOURCE inputs are not reread.",
        "frames": [{"frame": frame, "source": item["source"], "source_sha256": sha(data),
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
    parser.add_argument("--frame", type=int, help="Explicit frame: 0 or 15")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--source", help="Explicit PNG basename in this authoring folder; requires --prepare")
    parser.add_argument("--recipe", type=Path, help="Explicit saved recipe for reproduction")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    print("WITNESS export.py SHA256=" + sha(Path(__file__).read_bytes()), flush=True)
    try:
        check_frame(args.frame)
        require((args.prepare and args.source is not None and args.recipe is None) or
                (not args.prepare and args.source is None and args.recipe is not None),
                "explicit-input")
        require(not args.output.exists(), "output-already-exists")
        if args.prepare:
            recipe = prepare(args.frame, args.source)
            recipe_bytes = (json.dumps(recipe, indent=2) + "\n").encode("utf-8")
        else:
            recipe_bytes = args.recipe.read_bytes()
            recipe = json.loads(recipe_bytes)
        images, report = render(recipe, args.frame, args.preview_only)
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
    print(f"PASS remaining-wait{args.frame:03}; " + ("PREVIEW ONLY: runtime sprite not written" if args.preview_only
                                  else "runtime-canvas candidate written; not promoted"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
