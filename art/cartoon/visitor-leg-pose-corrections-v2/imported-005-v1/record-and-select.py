"""Record and select the user's cleaned 005 drawing. Image operations are in clean-source.ps1."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
ROOT = FAMILY.parents[2]
SOURCE_ORIGIN = Path("C:/Users/Admin/AppData/Local/Temp/codex-clipboard-4bbe9603-9e08-417b-8030-967597a1c198.png")


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    source_path = HERE / "source-screenshot.png"
    output_path = HERE / "005-transparent-v1.png"
    assert source_path.read_bytes() == SOURCE_ORIGIN.read_bytes()
    with Image.open(source_path) as im:
        source = np.array(im.convert("RGB"))
    with Image.open(HERE / "005-dot-repaired-v1.png") as im:
        repaired = np.array(im.convert("RGB"))
    with Image.open(output_path) as im:
        mode, canvas = im.mode, list(im.size)
        output = np.array(im.convert("RGBA"))
    assert source.shape == repaired.shape == output[:, :, :3].shape
    expected = np.zeros(source.shape[:2], dtype=bool)
    expected[141, 197:200] = True
    expected[145, 197:200] = True
    expected[142:145, 196:201] = True
    changed = np.any(source != repaired, axis=2)
    assert np.array_equal(changed, expected), "The repair changed pixels outside the 21-pixel dot"
    alpha = output[:, :, 3]
    visible = alpha > 0
    assert np.array_equal(output[:, :, :3][visible], repaired[visible])
    assert not alpha[109, 34] and not alpha[120, 30]
    # White cream and bottle highlights remain opaque.
    assert alpha[124, 54] == 255 and alpha[112, 52] == 255
    ys, xs = np.where(alpha >= 8)
    image_stats = {
        "canvas": canvas, "mode": mode,
        "alpha_range": [int(alpha.min()), int(alpha.max())],
        "alpha8_bounds": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "edge_alpha_max": int(max(alpha[0].max(), alpha[-1].max(), alpha[:, 0].max(), alpha[:, -1].max())),
        "background": "Transparent"
    }
    record = {
        "schema_version": 1, "resource": "SSUZY1.BMP", "frame": "005", "version": 1,
        "tool": "ImageMagick 7.1.2-24", "mode": "direct-screenshot-cleanup",
        "kind": "imported_screenshot_cutout",
        "method": "User-supplied elbow-corrected drawing. Removed the accidental red dot with a 21-pixel local skin-color interpolation and removed the pale checkerboard into transparency. Original 349 by 206 pixel scale and pose retained; no generation or resizing.",
        "output": pin(output_path),
        "references": [pin(source_path)],
        "source_origin": str(SOURCE_ORIGIN),
        "source_roles": ["User-selected finished 005 drawing, immutable source screenshot"],
        "transforms": {"scale": [1, 1], "translation": [0, 0], "rotation_degrees": 0, "crop": None},
        "repair": {
            "bounds_xyxy_exclusive": [196, 141, 201, 146], "changed_pixel_count": int(changed.sum()),
            "row_spans_inclusive": [{"y": 141, "x": [197, 199]}, {"y": 142, "x": [196, 200]},
                                    {"y": 143, "x": [196, 200]}, {"y": 144, "x": [196, 200]},
                                    {"y": 145, "x": [197, 199]}],
            "method": "Horizontal interpolation between neighboring unaffected skin colors at x=196/200 for rows 141/145, and x=195/201 for rows 142-144."
        },
        "background_removal": {
            "candidate_rule": "r>0.60 and g>0.60 and b>0.50 and max(r,g,b)-min(r,g,b)<0.16, normalized RGB",
            "flood_seeds_xy": [[0, 0], [34, 109], [30, 120]],
            "enclosed_background_pixels_removed": 10,
            "white_cream_preserved": True,
            "description": "Remove the edge-connected pale background and the small enclosed gap beneath the bottle hand. Preserve the separate white cream component."
        },
        "processing_script": pin(HERE / "clean-source.ps1"),
        "alpha_mask": pin(HERE / "foreground-alpha.png"),
        "image": image_stats,
        "pixel_check": {
            "source_copy_byte_identical": True,
            "total_source_pixels": int(alpha.size),
            "repaired_pixels": int(changed.sum()),
            "different_rgb_pixels_outside_repair": int(np.any(source != repaired, axis=2)[~expected].sum()),
            "retained_pixels": int(visible.sum()),
            "transparent_pixels": int((~visible).sum()),
            "different_retained_rgb_pixels_vs_repaired_source": int(np.any(output[:, :, :3] != repaired, axis=2)[visible].sum())
        },
        "selection_instruction_exact": "here is your new 005 with the elbow fixed, do what you need to and make that the updated image resource",
        "cleanup_instruction_exact": 'remove the red "dot" on her leg, thats my fault.',
        "approval_scope": "User-selected finished 005 drawing with the requested accidental-dot cleanup and transparent background.",
        "production_integrated": False, "native_motion_checked": False
    }
    save(HERE / "record.json", record)
    visual = {
        "schema_version": 1, "frame": "SSUZY1.BMP-005", "status": "user_selected_cleaned",
        "output": record["output"], "dark_proof": pin(HERE / "dark-proof.png"),
        "observations": [
            "The red annotation dot is gone; the repair blends into the neighboring skin.",
            "The supplied elbow, body, sunblock action, hips and leg arrangement are unchanged.",
            "The checkerboard and small enclosed gap under the bottle hand are transparent.",
            "The white cream and bottle highlights remain present.",
            "Viewed at native size and on a dark solid background enlarged three times. Screenshot-resolution antialiasing remains; no sharpening or repainting was applied."
        ],
        "image": image_stats, "appearance_basis": "Explicit user selection of the supplied drawing"
    }
    save(HERE / "visual-review.json", visual)

    selection_path = FAMILY / "selected-versions.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    before = copy.deepcopy(selection)
    feedback_path = FAMILY / "feedback-imported-005-v1.json"
    feedback = {
        "schema_version": 1, "date": "2026-09-21", "frame": "SSUZY1.BMP-005",
        "user_request_exact": record["selection_instruction_exact"],
        "cleanup_request_exact": record["cleanup_instruction_exact"],
        "appearance_selection": "Use the user's supplied elbow-corrected 005 drawing, cleaned of the accidental red dot.",
        "approval_scope": record["approval_scope"],
        "output": record["output"], "artifact_record": pin(HERE / "record.json"),
        "source_screenshot": pin(source_path),
        "previous_005_selection": before["frames"]["SSUZY1.BMP-005"],
        "production_integrated": False, "native_motion_checked": False
    }
    assert not feedback_path.exists(), "Selection already recorded"
    save(feedback_path, feedback)
    state = selection["frames"]["SSUZY1.BMP-005"]
    for version in (3, 4):
        if not any(entry.get("version") == version for entry in state["history"]):
            state["history"].append({
                "version": version, "status": "blocked",
                "request": pin(FAMILY / f"generation/SSUZY1.BMP/005-v{version}-request.json"),
                "failure": pin(FAMILY / f"generation/SSUZY1.BMP/005-v{version}-failure.json")
            })
    state.update(
        display_version=None, review_status="approved_by_user",
        latest_version=4, latest_status="blocked",
        display_label="Selected 005 drawing",
        status_text="The user's elbow-corrected 005 drawing is selected. The accidental red dot has been removed and the checkerboard is now transparent.",
        requested_change="Use the supplied elbow-corrected 005 drawing and remove the accidental red dot from the leg.",
        display_artifact={"kind": "imported_screenshot_cutout", "version": 1,
                          "title": "Selected 005 drawing", "record": pin(HERE / "record.json")},
        appearance_approval={"record": pin(feedback_path), "scope": record["approval_scope"],
                             "output": record["output"], "artifact_kind": "imported_screenshot_cutout", "version": 1},
        instruction_references=[{**pin(source_path), "label": "User-supplied 005 before dot cleanup"}],
        latest_feedback=pin(feedback_path),
        comparison_previous=pin(FAMILY / "generation/SSUZY1.BMP/005-generated-v2.png"),
        previous_label="Previous partial 005 v2",
        related_evidence=[{**pin(HERE / "visual-review.json"), "label": "Selected 005 cleanup inspection"},
                          {**pin(HERE / "dark-proof.png"), "label": "Transparent cutout on dark background"}]
    )
    state.pop("no_image_text", None)
    selection.update(
        status="all_seven_appearance_approved",
        selection_scope="All seven selected visitor drawings have appearance approval. 004 and 005 use user-selected screenshot cutouts with transparent backgrounds; 005 also has the accidental red dot removed. Native registration and production integration are not included.",
        latest_feedback=pin(feedback_path)
    )
    selection["appearance_approval"]["scope"] = "Five earlier drawing approvals plus the user-selected transparent 004 and 005 drawings."
    selection["appearance_approval"]["approved_frames"] = ["003", "004", "005", "006", "008", "009", "010"]
    selection["appearance_approval"].setdefault("additional_approval_records", []).append(pin(feedback_path))
    for key, value in before["frames"].items():
        if key != "SSUZY1.BMP-005":
            assert selection["frames"][key] == value, key
    save(selection_path, selection)
    print(json.dumps({"output": record["output"], "image": image_stats, "pixel_check": record["pixel_check"],
                      "status": selection["status"], "other_six_frame_entries_unchanged": True}))


if __name__ == "__main__":
    main()
