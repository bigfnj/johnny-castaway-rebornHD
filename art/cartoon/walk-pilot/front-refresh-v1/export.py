"""Freeze and reproduce an explicitly selected six-frame technical candidate.

Every --source is FRAME=approved or FRAME=RAW.png (relative to this folder).
Approved entries copy their exact runtime PNG bytes. New entries use a common
0.1 scale and an observed cap outline mapped to the earlier recipe's target.
Outputs retain their input bytes; neither this tool nor its recipes approve art.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import zipfile

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FRAMES = list(range(24, 30))
PAD = 64
SCALE = .1
OLD = "art/cartoon/walk-pilot/calm-focus-runtime-v1"
FILTERS = {"working_mode": "RGBa", "affine_filter": "BICUBIC", "oversample": 8,
           "downsample_filter": "LANCZOS", "output_mode": "RGBA", "png_compress_level": 9}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def encode(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def png(image):
    out = io.BytesIO()
    image.save(out, format="PNG", compress_level=9)
    return out.getvalue()


def decoded(raw, label, size=None):
    image = Image.open(io.BytesIO(raw))
    require(image.mode == "RGBA" and (size is None or list(image.size) == list(size)), label)
    image.load()
    return image


def cap_outline(image):
    alpha = image.getchannel("A")
    box = alpha.point(lambda n: 255 if n >= 128 else 0).getbbox()
    require(box is not None and box[1] < 300, "cap-outline-not-found")
    xs = [x for x in range(image.width) if alpha.getpixel((x, box[1])) >= 128]
    return [(min(xs) + max(xs) + 1) / 2, box[1]]


def prepare(sources, preview_only=False, root=ROOT, here=HERE):
    require(sorted(sources) == FRAMES, "six-explicit-sources-required")
    inputs = {"inputs/reference.json": (here / "reference/source.json").read_bytes(),
              "inputs/approved-recipe.json": (root / OLD / "recipe.json").read_bytes(),
              "inputs/original-catalog.json": (root / "docs/knowledge-base/cartoon-original-reference.json").read_bytes(),
              "inputs/walk-data.h": (root / "src/data/walk_data.h").read_bytes()}
    reference = json.loads(inputs["inputs/reference.json"])
    old = json.loads(inputs["inputs/approved-recipe.json"])
    refs = {row["frame"]: row for row in reference["frames"]}
    prior = {row["frame"]: row for row in old["frames"]}
    raw_bundle = (root / OLD / "source-images.zip").read_bytes()
    require(sha(raw_bundle) == old["source_bundle"]["sha256"], "approved-source-bundle-identity")
    recipe = {"schema_version": 1, "scope": "Technical candidate only; human approval and production promotion are not assigned.",
              "preview_only": bool(preview_only), "scale_exact": {"numerator": 1, "denominator": 10},
              "normalization": "none", "padding_hd": PAD, "resampling": FILTERS,
              "pillow_version": PIL.__version__, "frames": [],
              "cap_measurement": "Generated sources: first alpha-128 row's horizontal pixel-edge midpoint and row top. An outline observation, not an engine or anatomical anchor. Retained sources keep their historical manual registration."}
    with zipfile.ZipFile(root / "assets/scrantic_data.zip") as archive, zipfile.ZipFile(io.BytesIO(raw_bundle)) as bundle:
        for frame in FRAMES:
            record, previous = refs[frame], prior[frame]
            native = (here / "reference" / record["native"]).read_bytes()
            baseline = archive.read("data/styles/cartoon/" + previous["path"])
            raw = bundle.read(previous["generated_image"]) if sources[frame] == "approved" else (here / sources[frame]).read_bytes()
            require(sha(baseline) == previous["candidate_png_sha256"], f"approved-runtime-identity:{frame:03}")
            mode = "retained" if sources[frame] == "approved" else "generated"
            image = decoded(raw, f"source-canvas:{frame:03}", [1024, 1536])
            cap = previous["cap_raw"] if mode == "retained" else cap_outline(image)
            target = previous["cap_target_hd"]
            affine = previous["affine_forward"] if mode == "retained" else [SCALE, 0, target[0] - cap[0] * SCALE, 0, SCALE, target[1] - cap[1] * SCALE]
            row = {"frame": frame, "path": previous["path"], "mode": mode,
                   "source": f"inputs/raw/{frame:03}.png", "source_sha256": sha(raw),
                   "source_selection": str(sources[frame]), "baseline": f"inputs/baseline/{frame:03}.png",
                   "baseline_sha256": sha(baseline), "original": f"inputs/original/{frame:03}.png",
                   "generated_canvas": [1024, 1536], "runtime_canvas": previous["runtime_canvas"],
                   "cap_raw": cap, "cap_target_hd": target, "affine_forward": affine}
            inputs.update({row["source"]: raw, row["baseline"]: baseline, row["original"]: native})
            recipe["frames"].append(row)
    recipe["input_sha256"] = {name: sha(raw) for name, raw in sorted(inputs.items())}
    images, report = render(recipe, inputs, verify_outputs=False)
    recipe["output_sha256"] = {name: sha(raw) for name, raw in sorted(images.items())}
    for row in recipe["frames"]:
        if not preview_only:
            row["candidate_png_sha256"] = sha(images[row["path"]])
    return recipe, inputs, images, report


def render(recipe, inputs, verify_outputs=True):
    require(set(inputs) == set(recipe["input_sha256"]) and all(sha(raw) == recipe["input_sha256"][name] for name, raw in inputs.items()), "frozen-input-identity")
    require(recipe["schema_version"] == 1 and recipe["scale_exact"] == {"numerator": 1, "denominator": 10}
            and recipe["normalization"] == "none" and recipe["padding_hd"] == PAD
            and recipe["resampling"] == FILTERS and recipe["pillow_version"] == PIL.__version__
            and type(recipe["preview_only"]) is bool, "family-render-contract")
    require([row["frame"] for row in recipe["frames"]] == FRAMES, "six-explicit-sources-required")
    refs = json.loads(inputs["inputs/reference.json"])
    require(sha(inputs["inputs/approved-recipe.json"]) == refs["approved_recipe_sha256"]
            and sha(inputs["inputs/original-catalog.json"]) == refs["original_catalog_sha256"], "reference-authority-identity")
    originals = json.loads(inputs["inputs/original-catalog.json"])["assets"]
    refs = {row["frame"]: row for row in refs["frames"]}
    old = {row["frame"]: row for row in json.loads(inputs["inputs/approved-recipe.json"])["frames"]}
    images, reports = {}, []
    for row in recipe["frames"]:
        frame, previous, reference = row["frame"], old[row["frame"]], refs[row["frame"]]
        path = f"BMP/JOHNWALK.BMP/{frame:03}.png"
        require(row["path"] == path and row["mode"] in ("retained", "generated"), f"frame-contract:{frame:03}")
        native = decoded(inputs[row["original"]], f"original-canvas:{frame:03}")
        require(sha(inputs[row["original"]]) == reference["native_sha256"]
                and sha(native.tobytes()) == originals[path]["rgba_sha256"], f"original-identity:{frame:03}")
        canvas = [native.width * 2, native.height * 2]
        require(row["runtime_canvas"] == canvas == previous["runtime_canvas"], f"runtime-canvas:{frame:03}")
        baseline = decoded(inputs[row["baseline"]], f"baseline-canvas:{frame:03}", canvas)
        require(sha(inputs[row["baseline"]]) == row["baseline_sha256"] == previous["candidate_png_sha256"], f"approved-runtime-identity:{frame:03}")
        source = decoded(inputs[row["source"]], f"source-canvas:{frame:03}", [1024, 1536])
        require(row["generated_canvas"] == [1024, 1536] and sha(inputs[row["source"]]) == row["source_sha256"], f"source-identity:{frame:03}")
        cap = previous["cap_raw"] if row["mode"] == "retained" else cap_outline(source)
        target = previous["cap_target_hd"]
        tx, ty = target[0] - cap[0] * SCALE, target[1] - cap[1] * SCALE
        affine = [SCALE, 0, tx, 0, SCALE, ty]
        require(row["cap_raw"] == cap and row["cap_target_hd"] == target and len(row["affine_forward"]) == 6
                and all(math.isclose(a, b, rel_tol=0, abs_tol=1e-12) for a, b in zip(affine, row["affine_forward"])), f"fixed-registration:{frame:03}")
        if row["mode"] == "retained":
            require(row["source_sha256"] == reference["approved_raw_sha256"] == previous["source_sha256"], f"retained-source-identity:{frame:03}")
        bounds = source.getchannel("A").point(lambda n: 255 if n >= 8 else 0).getbbox()
        require(bounds is not None, f"empty-source:{frame:03}")
        centers = [(bounds[0] + .5) * SCALE + tx, (bounds[1] + .5) * SCALE + ty,
                   (bounds[2] - .5) * SCALE + tx, (bounds[3] - .5) * SCALE + ty]
        width, height = canvas
        fits = centers[0] >= 0 and centers[1] >= 0 and centers[2] < width and centers[3] < height
        require(recipe["preview_only"] or fits, f"runtime-overhang:{frame:03}")
        size = (width + PAD * 2, height + PAD * 2)
        if row["mode"] == "retained":
            padded = Image.new("RGBA", size)
            padded.paste(baseline, (PAD, PAD))
            runtime = inputs[row["baseline"]]
        else:
            high = source.convert("RGBa").transform((size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
                (1 / (SCALE * 8), 0, -(tx + PAD) / SCALE, 0, 1 / (SCALE * 8), -(ty + PAD) / SCALE),
                resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
            padded = high.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
            runtime = png(padded.crop((PAD, PAD, PAD + width, PAD + height)))
        filtered = padded.getchannel("A").point(lambda n: 255 if n >= 8 else 0).getbbox()
        images[f"padded/{frame:03}.png"] = png(padded)
        if not recipe["preview_only"]:
            images[path] = runtime
        reports.append({"frame": frame, "mode": row["mode"], "source_sha256": row["source_sha256"],
                        "runtime_canvas": canvas, "cap_raw": cap, "cap_target_hd": target,
                        "affine_forward": affine, "alpha8_source_bounds": list(bounds), "alpha8_centers_hd": centers,
                        "source_centers_fit_runtime": fits, "overhang_hd_left_top_right_bottom":
                        [max(0, -centers[0]), max(0, -centers[1]), max(0, centers[2] - width), max(0, centers[3] - height)],
                        "filtered_alpha8_bounds_hd_exclusive": [filtered[0] - PAD, filtered[1] - PAD, filtered[2] - PAD, filtered[3] - PAD],
                        "runtime_png_sha256": sha(runtime), "padded_png_sha256": sha(images[f"padded/{frame:03}.png"]),
                        "retained_runtime_bytes_identical": runtime == inputs[row["baseline"]] if row["mode"] == "retained" else None})
    if verify_outputs:
        require({name: sha(raw) for name, raw in sorted(images.items())} == recipe["output_sha256"], "recorded-output-identity")
        require(recipe["preview_only"] or all(row.get("candidate_png_sha256") == sha(images[row["path"]]) for row in recipe["frames"]), "recorded-runtime-identity")
    return images, {"scope": "Technical export only; no visual acceptance or native rendering claim.",
                    "preview_only": recipe["preview_only"], "runtime_sprites_written": not recipe["preview_only"],
                    "runtime_fit_all_source_centers": all(row["source_centers_fit_runtime"] for row in reports),
                    "padding_hd": PAD, "frames": reports,
                    "filter_limit": "Alpha8 source-center fit does not promise absence of low-alpha filter fringes. Retained padded views contain exact existing runtime pixels, not a newly filtered raw source."}


def reproduce(recipe_path):
    recipe = json.loads(recipe_path.read_bytes())
    inputs = {}
    for name in recipe["input_sha256"]:
        require(name.startswith("inputs/") and not any(p in ("", ".", "..") for p in name.split("/")) and "\\" not in name and ":" not in name, "unsafe-input-path")
        inputs[name] = (recipe_path.parent / name).read_bytes()
    images, report = render(recipe, inputs)
    return recipe, inputs, images, report


def write_output(output, recipe, inputs, images, report):
    require(not output.exists(), "output-already-exists")
    output.mkdir(parents=True)
    for name, raw in {**inputs, **images, "recipe.json": encode(recipe), "export-report.json": encode(report)}.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    print("WITNESS front-export " + sha(Path(__file__).read_bytes()), flush=True)
    try:
        require(not args.output.exists(), "output-already-exists")
        require(bool(args.source) != bool(args.recipe), "choose-sources-or-recipe")
        if args.recipe:
            require(not args.preview_only, "saved-recipe-controls-preview-mode")
            result = reproduce(args.recipe)
        else:
            entries = [entry.split("=", 1) for entry in args.source]
            require(len(entries) == 6 and all(len(entry) == 2 for entry in entries), "six-explicit-sources-required")
            sources = {int(frame): path for frame, path in entries}
            result = prepare(sources, args.preview_only)
        write_output(args.output, *result)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS six technical sources exported; " + ("PREVIEW ONLY" if result[0]["preview_only"] else "runtime candidates, not promoted"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
