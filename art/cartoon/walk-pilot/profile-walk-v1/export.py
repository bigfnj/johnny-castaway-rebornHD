"""Export one explicit profile-walk pose (001-008) at fixed family scale.

Adapted from front-arrival-v1/remaining-waits-v1/export.py; approved tools stay
unchanged. The premultiplied filter/placement algorithm is retained exactly.

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
TARGETS = {
    1: [72, .25], 2: [70, .25], 3: [54, .25], 4: [66, .25],
    5: [74, .25], 6: [70, .25], 7: [48, .25], 8: [62, .25],
}
FILTERS = {"working_mode": "RGBa", "affine": "BICUBIC", "oversample": 8,
           "downsample": "LANCZOS", "output_mode": "RGBA", "png_compress_level": 9}
REFERENCE_HASHES = {
    1: {
        "001-source.json": "550ba848889a690bb016acf97e09011b2a8c10f7b1e474e8d1dbfdc1c674b053",
        "001-original-native.png": "a8eccac35a1f596717fd9e8494ee6aec7d1188eb894b664a25cadba6d5620bdf",
        "001-original-nearest8.png": "6e9d3529acef2cd7fc95b5ee03f65a9a017d054f428ef1b34799769e2a34b8b7",
    },
    2: {
        "002-source.json": "63e6962d70779ccbc5553ef2cf3523fbf58e5f211ba8f545b496fedd6d0e437e",
        "002-original-native.png": "c1629bd15af61911ebf7e73f3a95a97e3322b5eb0a603ff8b3cceafeb644079c",
        "002-original-nearest8.png": "ac6cc66fe1f3edaa66b19e5857f238c5abb70ad4fec188afe9d56ada2f97198f",
    },
    3: {
        "003-source.json": "6e623fdca7729dd52f1f0667cd9b248b788bf3574196dce5f02e4f4544acb15d",
        "003-original-native.png": "622f8902c51975a70498fa7630969c637f979207ac206d43af77dd621d8f2310",
        "003-original-nearest8.png": "7d3aad1acabbebd015c224fd85e0c53772fe564a420426cdfd14d7092fa0374b",
    },
    4: {
        "004-source.json": "8efcf4fe1be92c13c6734cb498d091d70a5256d756b857ff48b8bcc295d37173",
        "004-original-native.png": "3cf353a0cb04b9cd800bc6639cb012d82717d7d02be96d1d9fac92b009b80a15",
        "004-original-nearest8.png": "f0563be7873e711739211afc1b5d66752d2a0741f077b73fb586562ea3ed99ca",
    },
    5: {
        "005-source.json": "17675c54b57ab106765b42f6e6710bb62cae50b01f66a858ba3e8f6d47403ee0",
        "005-original-native.png": "3e4c61d33125003225512f41c61ad89342d191492998e98d93c2dfd3e62f006f",
        "005-original-nearest8.png": "f90926644cf67d549c5ffd5e3129bacd8cad43aa833ed2ebce3c08a59bd4a9cb",
    },
    6: {
        "006-source.json": "f53a690d70ef29bdbd9a6693ba9dc097963c2008b444b451116707f8031511e2",
        "006-original-native.png": "ab03f6386c4d3e02b865d1991b7c3dd6fa6eb9809322df651aee7423c549ca72",
        "006-original-nearest8.png": "1269b4c701df5b5e31b7fec133ea1843e88bcfe3e1ae8a6476b1443766032e5d",
    },
    7: {
        "007-source.json": "6a04e4906b9817c652fb1bb9d7c6a309d2516075259ce74c5156b7efde2644c9",
        "007-original-native.png": "8f56b47bd0f6087c0e4ebaeebf1d352adb96fbf1ba5799f10e301876d899ace2",
        "007-original-nearest8.png": "14dc2e96394f8c4604f1fa084c84e6c70ceede645db8b3d95074980a745b10c3",
    },
    8: {
        "008-source.json": "2e7894606c061d54e32e5abae507723dff3905248b40a8503aa34127cf94bbef",
        "008-original-native.png": "9a1675829c300e3dcf493134f800b5e9a35b3b5cd533add592f37384bd12d693",
        "008-original-nearest8.png": "1c0b183d0d6378ec00ca1b8f9b455fc26b25add8efcca991ac31022990e2b9dc",
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
    require(type(frame) is int and frame in TARGETS, "allowed-frame")


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
        "scope": f"Technical profile-walk-{frame:03} review only; no runtime or motion approval.",
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
    parser.add_argument("--frame", type=int, help="Explicit profile frame: 1 through 8")
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
    print(f"PASS profile-walk{args.frame:03}; " + ("PREVIEW ONLY: runtime sprite not written" if args.preview_only
                                  else "runtime-canvas candidate written; not promoted"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
