"""Preserve the displayed review and reopen only the two requested corrections."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    feedback_path = HERE / "feedback-004-proportions-005-elbow-v1.json"
    assert not feedback_path.exists(), "Feedback already recorded; do not repeat the snapshot."
    selection = json.loads((HERE / "selected-versions.json").read_text(encoding="utf-8"))
    before = copy.deepcopy(selection)
    snapshot_dir = HERE / "feedback-004-proportions-005-elbow-v1"
    snapshot_dir.mkdir(exist_ok=False)
    snapshots = []
    for name in ("review.html", "review-data.json", "review-record.json", "selected-versions.json",
                 "review-template.html", "review.js", "build_review.py", "session-status.md",
                 "pose-regeneration-notes.md"):
        src = HERE / name
        dest = snapshot_dir / name
        shutil.copyfile(src, dest)
        snapshots.append({"source_path": src.relative_to(ROOT).as_posix(), "snapshot": pin(dest)})
    composite_record = HERE / "direct-composite-004-v1/record.json"
    composite = json.loads(composite_record.read_text(encoding="utf-8"))
    previous_005 = selection["frames"]["SSUZY1.BMP-005"]["appearance_approval"]
    approval = copy.deepcopy(selection["appearance_approval"])
    unchanged_frames = ["003", "006", "008", "009", "010"]
    feedback = {
        "schema_version": 1,
        "date": "2026-09-21",
        "frames": ["SSUZY1.BMP-004", "SSUZY1.BMP-005"],
        "user_request_exact": "given the pushback, i still want to make one more attempt at fixing 004 and a correction to 005. 004, the stomach section looks overly elongated, maybe now that we have the top and legs fixed, we can generate the body proportions more accurately. for 005, she is leaning on her elbow and holding the sunblock to squeeze it into her lower hand. Specifically we need to have her leaning on her elbow, move the sunblock to the other hand. make sense ?",
        "instruction_authority": "Latest user correction reopens 005's posture and bottle action and requests 004 torso proportions from the direct composite. Earlier appearance approvals are retained as history.",
        "corrections": {
            "004": {"requested_change": "Shorten the overly elongated stomach section for natural body proportions while preserving the corrected head, upper body identity, hips and leg arrangement.",
                    "edit_target": composite["output"], "edit_target_record": pin(composite_record),
                    "appearance_approval": None},
            "005": {"requested_change": "Lean on the elbow. Move the sunblock to the other, upper hand and tip it to squeeze into the lower hand.",
                    "edit_target": previous_005["output"],
                    "original_pose_reference": pin(ROOT / "art/cartoon/workers-and-mermaids-batch-v1/reference/nearest8/SSUZY1.BMP/005.png"),
                    "previous_appearance_approval": previous_005, "approval_reopened": True}
        },
        "shown_review_snapshots": snapshots,
        "prior_batch_approval": approval,
        "unchanged_approved_frames": unchanged_frames,
        "production_integrated": False,
        "native_motion_checked": False
    }
    save(feedback_path, feedback)
    feedback_pin = pin(feedback_path)
    state4 = selection["frames"]["SSUZY1.BMP-004"]
    state4["history"].append({"version": 8, "status": "blocked",
                              "request": pin(HERE / "generation/SSUZY1.BMP/004-v8-request.json"),
                              "failure": pin(HERE / "generation/SSUZY1.BMP/004-v8-failure.json")})
    state4["artifact_history"] = state4.get("artifact_history", []) + [{
        "kind": "direct_png_composite", "version": 1, "status": "correction_requested",
        "reason": "User says the stomach section is overly elongated; the head and leg arrangement are the basis for the proportion correction.",
        "record": pin(composite_record), "output": composite["output"], "feedback": feedback_pin}]
    state4.update(review_status="awaiting_correction",
                  status_text="A torso-proportion correction was requested from this direct composite. The head and leg arrangement are retained as the reference.",
                  requested_change=feedback["corrections"]["004"]["requested_change"],
                  comparison_previous=composite["output"], previous_label="Previous direct composite",
                  latest_feedback=feedback_pin,
                  instruction_references=[{**composite["output"], "label": "004 direct composite: head and leg arrangement"}])
    state5 = selection["frames"]["SSUZY1.BMP-005"]
    state5["appearance_approval_history"] = state5.get("appearance_approval_history", []) + [{
        **copy.deepcopy(previous_005), "status": "reopened_for_correction", "feedback": feedback_pin}]
    state5["history"] = state5.get("history", []) + [{
        "version": 1, "status": "reopened_for_correction", "output": previous_005["output"],
        "request": pin(HERE / "generation/SSUZY1.BMP/005-v1-request.json"),
        "record": pin(HERE / "generation/SSUZY1.BMP/005-record-v1.json"),
        "appearance_approval": copy.deepcopy(previous_005), "feedback": feedback_pin}]
    state5.update(review_status="awaiting_correction", appearance_approval=None,
                  status_text="Earlier v1 approval is preserved in history. The user reopened 005 to correct elbow support and the sunblock hand/action.",
                  requested_change=feedback["corrections"]["005"]["requested_change"],
                  comparison_previous=previous_005["output"], previous_label="Previously approved v1",
                  latest_feedback=feedback_pin,
                  instruction_references=[{**feedback["corrections"]["005"]["original_pose_reference"],
                                           "label": "005 original: elbow support and bottle action"}])
    selection["appearance_approval_history"].append({**approval, "status": "005_reopened_by_later_feedback", "feedback": feedback_pin})
    selection["appearance_approval"] = {**approval, "scope": "Full appearance of the five unchanged selected drawings. 005's earlier approval is preserved historically and reopened for correction.",
                                       "approved_frames": unchanged_frames}
    selection.update(status="five_approved_004_005_corrections_pending",
                     selection_scope="003, 006, 008, 009 and 010 remain appearance approved. 004 torso proportions and 005 elbow support/bottle action are awaiting correction.",
                     latest_feedback=feedback_pin)
    for frame in unchanged_frames:
        assert selection["frames"][f"SSUZY1.BMP-{frame}"] == before["frames"][f"SSUZY1.BMP-{frame}"]
    save(HERE / "selected-versions.json", selection)
    print(json.dumps({"feedback": feedback_pin, "unchanged_approved_frames": unchanged_frames}))


if __name__ == "__main__":
    main()
