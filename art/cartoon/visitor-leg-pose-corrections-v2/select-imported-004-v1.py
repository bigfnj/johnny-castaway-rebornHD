"""Record the user's selected screenshot crop as 004's appearance."""
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
    record_path = HERE / "imported-004-v1/record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert pin(ROOT / record["output"]["path"]) == record["output"]
    feedback_path = HERE / "feedback-imported-004-v1.json"
    assert not feedback_path.exists()
    feedback = {
        "schema_version": 1, "date": "2026-09-21", "frame": "SSUZY1.BMP-004",
        "user_request_exact": "can you crop out and use the right image for 004 ?",
        "appearance_selection": "Use the right-hand drawing in the user-supplied screenshot for 004.",
        "approval_scope": record["approval_scope"],
        "output": record["output"], "artifact_record": pin(record_path),
        "source_screenshot": record["references"][0],
        "previous_004_selection": before["frames"]["SSUZY1.BMP-004"],
        "background": record["image"]["background"],
        "production_integrated": False, "native_motion_checked": False
    }
    save(feedback_path, feedback)
    approval = {"record": pin(feedback_path), "scope": record["approval_scope"],
                "output": record["output"], "artifact_kind": "imported_screenshot_crop", "version": 1}
    state = selection["frames"]["SSUZY1.BMP-004"]
    state.update(display_version=None, review_status="approved_by_user", display_label="Selected 004 drawing",
                 status_text="The user selected this right-hand screenshot drawing for 004. It is an exact crop with the screenshot's opaque checkerboard retained.",
                 requested_change="Crop the right-hand drawing from the supplied screenshot and use it for 004.",
                 display_artifact={"kind": "imported_screenshot_crop", "version": 1,
                                   "title": "Selected 004 drawing", "record": pin(record_path)},
                 appearance_approval=approval,
                 instruction_references=[{**record["references"][0], "label": "User-supplied screenshot"}],
                 latest_feedback=pin(feedback_path))
    state.pop("no_image_text", None)
    selection.update(status="six_approved_005_incomplete",
                     selection_scope="004 uses the user-selected screenshot crop for appearance. 003, 006, 008, 009 and 010 retain their earlier approvals. 005 remains unchanged as a partial correction. Native transparency and production integration are not included.",
                     latest_feedback=pin(feedback_path))
    selection["appearance_approval"]["scope"] = "Five earlier drawing approvals plus the user-selected imported 004 screenshot appearance. 005 remains reopened."
    selection["appearance_approval"]["approved_frames"] = ["003", "004", "006", "008", "009", "010"]
    selection["appearance_approval"]["additional_approval_records"] = [pin(feedback_path)]
    for key, value in before["frames"].items():
        if key != "SSUZY1.BMP-004":
            assert selection["frames"][key] == value, key
    save(HERE / "selected-versions.json", selection)
    print(json.dumps({"status": selection["status"], "selected_004": record["output"],
                      "other_six_frame_entries_unchanged": True}))


if __name__ == "__main__":
    main()
