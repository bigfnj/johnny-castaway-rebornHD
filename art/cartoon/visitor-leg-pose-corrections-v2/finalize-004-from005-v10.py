"""Record the unavailable 004 v10 edit without changing any other selection."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    selection_path = HERE / "selected-versions.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    feedback_path = HERE / "feedback-004-from005-v10.json"
    feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
    folder = HERE / "generation/SSUZY1.BMP"
    failure = json.loads((folder / "004-v10-failure.json").read_text(encoding="utf-8-sig"))
    assert failure["image_returned"] is False
    assert not (folder / "004-generated-v10.png").exists()
    state = selection["frames"]["SSUZY1.BMP-004"]
    assert state["latest_version"] == 9, "Expected the preceding v9 state."
    state["history"].append({"version": 9, "status": "blocked",
                             "request": pin(folder / "004-v9-request.json"),
                             "failure": pin(folder / "004-v9-failure.json")})
    state.update(latest_version=10, latest_status="blocked", review_status="awaiting_correction",
                 status_text="The new 004 request used 005's sunblock action and 003's lowered reclining legs, but returned no image. No replacement drawing is available.",
                 requested_change="Use 005 v2's sunblock hand action and upper body, with the raised leg lowered to the reclining hip and leg arrangement in approved 003 v2.",
                 no_image_text="The 004 v10 request based on 005 and 003 returned no image. The 005 starting drawing is shown at left; no new 004 was produced.",
                 comparison_previous=pin(folder / "005-generated-v2.png"),
                 previous_label="005 v2 starting drawing",
                 instruction_references=feedback["ordered_image_references"],
                 latest_feedback=pin(feedback_path))
    selection.update(status="five_approved_004_005_incomplete",
                     selection_scope="003, 006, 008, 009 and 010 remain appearance approved. Latest 004 v10 returned no image. 005 remains the same partial v2 correction with its later v3 attempt blocked.",
                     latest_feedback=pin(feedback_path))
    unchanged = {key: value for key, value in selection["frames"].items() if key != "SSUZY1.BMP-004"}
    assert hashlib.sha256(json.dumps(unchanged, sort_keys=True).encode()).hexdigest() == feedback["unchanged_other_frame_selections_sha256"]
    selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"latest_004_version": 10, "latest_004_status": "blocked", "other_six_frame_entries_unchanged": True}))


if __name__ == "__main__":
    main()
