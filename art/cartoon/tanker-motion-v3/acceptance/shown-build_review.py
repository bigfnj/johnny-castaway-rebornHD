"""Bind exact drafts for the source-derived tanker comparison. Never edits PNGs."""
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EARLIER = HERE.parent / "tanker-motion-v2/sprites.json"
SEQUENCE = HERE.parent / "tanker-motion-v1/source-sequence.json"
GENERATION = ROOT / "art/cartoon/tanker-v1/generation/TANKER.BMP"

# Explicit draft selection. Change only the requested frame when a revision arrives.
REVISED = {
    0: 4, 1: 4, 2: 4, 3: 3, 4: 3, 5: 4, 6: 3,
    7: 2, 8: 2, 9: 3, 10: 2, 11: 2, 12: 5, 13: 1,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path, expected=None):
    digest = sha(path)
    if expected is not None and digest != expected:
        raise ValueError(f"Earlier selection bytes changed: {path}")
    with Image.open(path) as image:
        if "A" not in image.getbands():
            raise ValueError(f"Alpha channel required: {path}")
        alpha = image.getchannel("A")
        box = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
        if box is None:
            raise ValueError(f"No visible artwork: {path}")
        size = list(image.size)
        alpha_extrema = list(alpha.getextrema())
    return {
        "url": os.path.relpath(path, HERE).replace(os.sep, "/"),
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest,
        "canvas": size,
        "bounds": list(box),
        "bounds_alpha_threshold": 8,
        "alpha_extrema": alpha_extrema,
    }


def ratios(row):
    original = row["original"]["bounds"]
    ow, oh = original[2] - original[0], original[3] - original[1]
    result = {}
    for role, value in row.items():
        box = value["bounds"]
        width, height = box[2] - box[0], box[3] - box[1]
        scale = min(ow / width, oh / height)
        result[role] = {
            "path": value["path"], "sha256": value["sha256"],
            "visible_size": [width, height],
            "visible_width_height_ratio": width / height,
            "ratio_relative_to_original": (width / height) / (ow / oh),
            "uniform_preview_scale": scale,
            "fitted_visible_size": [width * scale, height * scale],
            "fitted_width_fraction_of_original": width * scale / ow,
            "fitted_height_fraction_of_original": height * scale / oh,
        }
    return result


def save(path, data):
    path.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))


def main():
    revised_paths = {frame: GENERATION / f"{frame:03}-generated-v{version}.png"
                     for frame, version in REVISED.items()}
    missing = [str(path) for path in revised_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Selected final PNGs are not ready; no binding files written:\n" + "\n".join(missing))
    earlier = json.loads(EARLIER.read_bytes())
    source = json.loads(SEQUENCE.read_bytes())
    frames = {}
    for frame in range(14):
        old = earlier[str(frame)]
        frames[str(frame)] = {
            "original": bind(ROOT / old["original"]["path"], old["original"]["sha256"]),
            "earlier": bind(ROOT / old["cartoon"]["path"], old["cartoon"]["sha256"]),
            "revised": bind(revised_paths[frame]),
        }
    manifest = {
        "schema_version": 1,
        "status": "revised_yaw_draft_for_human_review_not_approved",
        "source_sequence": {"url": "../tanker-motion-v1/source-sequence.json",
                            "path": SEQUENCE.relative_to(ROOT).as_posix(), "sha256": sha(SEQUENCE)},
        "earlier_selection": {"path": EARLIER.relative_to(ROOT).as_posix(), "sha256": sha(EARLIER)},
        "revised_versions": REVISED,
        "draw_count": len(source["draws"]),
        "nominal_pass_ms": sum(row["nominal_duration_ms"] for row in source["draws"]),
        "fit": "Uniformly fit alpha>=8 visible bounds inside original visible bounds; center horizontally and align visible bottoms. Draw the complete source PNG without alpha cleanup or clipping.",
        "frames": frames,
    }
    diagnostics = {
        "status": "descriptive_measurements_only_not_a_gate_or_approval",
        "alpha_threshold": 8,
        "note": "Silhouette ratios include visible fittings and water. These measurements do not establish camera yaw, native placement or correct anatomy. Original/earlier/revised use exactly the review bindings.",
        "frames": {frame: ratios(row) for frame, row in frames.items()},
    }
    save(HERE / "sprites.json", manifest)
    diagnostics["sprites_sha256"] = sha(HERE / "sprites.json")
    save(HERE / "ratio-diagnostics.json", diagnostics)
    print(f"Bound 14 original/earlier/revised triples; {len(source['draws'])} source draws; PNGs unchanged")


if __name__ == "__main__":
    main()
