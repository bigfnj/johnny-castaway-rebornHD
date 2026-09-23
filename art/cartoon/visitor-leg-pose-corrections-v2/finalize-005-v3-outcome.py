"""Preserve the partial v2 candidate after the focused elbow edit returned no image."""
import copy
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
    before = copy.deepcopy(selection)
    folder = HERE / "generation/SSUZY1.BMP"
    failure = json.loads((folder / "005-v3-failure.json").read_text(encoding="utf-8-sig"))
    assert failure["image_returned"] is False
    assert not (folder / "005-generated-v3.png").exists()
    state = selection["frames"]["SSUZY1.BMP-005"]
    state["history"].append({"version": 2, "status": "diagnostic_insufficient",
                             "reason": "The bottle action is corrected, but the elbow is still too high relative to the resting hip and legs to read as bearing weight.",
                             "request": pin(folder / "005-v2-request.json"),
                             "record": pin(folder / "005-record-v2.json"),
                             "output": pin(folder / "005-generated-v2.png"),
                             "visual_review": pin(folder / "005-visual-review-v2.json")})
    state.update(display_version=2, display_label="Partial correction v2", review_status="awaiting_correction",
                 latest_version=3, latest_status="blocked", appearance_approval=None,
                 status_text="Partial correction: v2 moves the inverted bottle above the other cupped palm and bends the elbow, but the elbow remains too high to read as supporting her weight. The focused v3 edit returned no image; the support pose remains unresolved.",
                 related_evidence=[{"path": (folder / "005-visual-review-v2.json").relative_to(ROOT).as_posix(),
                                    "label": "005 v2 visual assessment: elbow support unresolved"}])
    selection.update(status="five_approved_004_005_incomplete",
                     selection_scope="003, 006, 008, 009 and 010 remain appearance approved. 004 torso proportions and 005 elbow support remain unresolved. 005 v2 is displayed as a partial correction; 004 v9 and 005 v3 returned no image.")
    for frame in ["003", "004", "006", "008", "009", "010"]:
        assert selection["frames"][f"SSUZY1.BMP-{frame}"] == before["frames"][f"SSUZY1.BMP-{frame}"]
    save(HERE / "selected-versions.json", selection)
    outcomes = json.loads((HERE / "004-proportions-005-elbow-outcomes.json").read_text(encoding="utf-8"))
    outcomes["005"] = {
        "displayed_version": 2, "displayed_status": "partial_correction", "displayed_image_returned": True,
        "request": pin(folder / "005-v2-request.json"), "record": pin(folder / "005-record-v2.json"),
        "output": pin(folder / "005-generated-v2.png"), "visual_review": pin(folder / "005-visual-review-v2.json"),
        "appearance_approval": None, "latest_version": 3, "latest_status": "blocked",
        "latest_image_returned": False, "latest_request": pin(folder / "005-v3-request.json"),
        "latest_failure": pin(folder / "005-v3-failure.json"),
        "unresolved": "The bent supporting elbow remains too high relative to the resting hip and legs to read as bearing weight."}
    save(HERE / "004-proportions-005-elbow-outcomes.json", outcomes)
    print(json.dumps({"status": selection["status"], "displayed_005_version": 2, "latest_005_version": 3}))


if __name__ == "__main__":
    main()
