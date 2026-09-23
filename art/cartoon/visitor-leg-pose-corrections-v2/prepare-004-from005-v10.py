"""Capture the user's new 004 direction without changing other frame selections."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    dest = HERE / "feedback-004-from005-v10.json"
    assert not dest.exists(), "Do not overwrite the captured feedback."
    selection = json.loads((HERE / "selected-versions.json").read_text(encoding="utf-8"))
    folder = HERE / "generation/SSUZY1.BMP"
    unchanged = {key: value for key, value in selection["frames"].items() if key != "SSUZY1.BMP-004"}
    value = {
        "schema_version": 1,
        "date": "2026-09-21",
        "frame": "SSUZY1.BMP-004",
        "user_request_exact": "can you use the prompt from 005 and have it lower the leg like in 003 and THAT can be our 004 ?",
        "required_change": "Use the successful 005 v2 prompt and drawing as the starting point, then lower the raised leg to the approved 003 v2 reclining leg pose to create 004.",
        "instruction_authority": "This latest 004 direction supersedes the prior direct-composite torso-proportion edit. It does not revise or approve 005.",
        "prompt_reference": pin(folder / "005-v2-request.json"),
        "ordered_image_references": [
            {**pin(folder / "005-generated-v2.png"), "label": "005 v2: starting drawing and bottle action"},
            {**pin(folder / "003-generated-v2.png"), "label": "Approved 003 v2: lowered reclining leg pose"}
        ],
        "previous_004_selection": copy.deepcopy(selection["frames"]["SSUZY1.BMP-004"]),
        "unchanged_other_frame_selections_sha256": hashlib.sha256(json.dumps(unchanged, sort_keys=True).encode()).hexdigest(),
        "appearance_approval": None,
        "production_integrated": False,
        "native_motion_checked": False
    }
    dest.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(pin(dest)))


if __name__ == "__main__":
    main()
