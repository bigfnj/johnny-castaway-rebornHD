"""Select the returned 005 edit and record the unavailable 004 proportion edit."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    selection = json.loads((HERE / "selected-versions.json").read_text(encoding="utf-8"))
    before = json.loads((HERE / "feedback-004-proportions-005-elbow-v1/selected-versions.json").read_text(encoding="utf-8"))
    folder = HERE / "generation/SSUZY1.BMP"
    failure = json.loads((folder / "004-v9-failure.json").read_text(encoding="utf-8-sig"))
    assert failure["image_returned"] is False
    assert not (folder / "004-generated-v9.png").exists()
    result = json.loads((folder / "005-record-v2.json").read_text(encoding="utf-8-sig"))
    assert pin(ROOT / result["output"]["path"]) == result["output"]
    state4 = selection["frames"]["SSUZY1.BMP-004"]
    state4.pop("display_artifact", None)
    state4.update(display_version=None, review_status="awaiting_correction", latest_version=9,
                  latest_status="blocked",
                  status_text="The torso-proportion edit returned no image. The earlier direct composite remains shown for comparison; its elongated stomach section is unresolved.",
                  no_image_text="The latest torso-proportion request returned no image. The earlier composite is preserved at left; no corrected replacement is available.")
    state5 = selection["frames"]["SSUZY1.BMP-005"]
    state5.update(display_version=2, review_status="ready_for_review", latest_version=2,
                  latest_status="returned", appearance_approval=None,
                  status_text="New v2 lowers the torso onto the supporting elbow and moves the inverted sunblock bottle to that raised hand, above the other cupped palm. Ready for appearance review.")
    selection.update(status="five_approved_005_review_004_unresolved",
                     selection_scope="003, 006, 008, 009 and 010 remain appearance approved. 005 v2 is ready for appearance review. 004's torso-proportion request returned no image and remains unresolved.")
    for frame in ["003", "006", "008", "009", "010"]:
        assert selection["frames"][f"SSUZY1.BMP-{frame}"] == before["frames"][f"SSUZY1.BMP-{frame}"]
    save(HERE / "selected-versions.json", selection)
    save(HERE / "004-proportions-005-elbow-outcomes.json", {
        "schema_version": 1,
        "feedback": pin(HERE / "feedback-004-proportions-005-elbow-v1.json"),
        "004": {"version": 9, "status": "blocked", "image_returned": False,
                "request": pin(folder / "004-v9-request.json"),
                "failure": pin(folder / "004-v9-failure.json"),
                "unresolved": "The direct composite's stomach section remains overly elongated."},
        "005": {"version": 2, "status": "ready_for_review", "image_returned": True,
                "request": pin(folder / "005-v2-request.json"),
                "record": pin(folder / "005-record-v2.json"), "output": result["output"],
                "appearance_approval": None},
        "unchanged_approved_frames": ["003", "006", "008", "009", "010"],
        "production_integrated": False, "native_motion_checked": False})
    print(json.dumps({"status": selection["status"], "005_output": result["output"]}))


if __name__ == "__main__":
    main()
