"""Record the user's scoped approval of SSUZY1 004 direct composite v3."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
VISITOR = HERE.parent
ROOT = VISITOR.parents[2]
KEY = "SSUZY1.BMP-004"
EXPECTED = "d53304f654f59676097bbbb15add2d54e8f503cd173511e59475c5cf5d2c957d"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    selection_path = VISITOR / "selected-versions.json"
    selection = read(selection_path)
    before = copy.deepcopy(selection)
    state = selection["frames"][KEY]
    image = pin(HERE / "004-composite-v3.png")
    assert image["sha256"] == EXPECTED
    artifact_record = read(HERE / "record.json")
    assert artifact_record["output"] == image
    acceptance_path = VISITOR / "acceptance/appearance-004-composite-v3.json"
    if not acceptance_path.exists():
        save(acceptance_path, {
            "schema_version": 1, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "frame": KEY, "version": 3, "artifact_kind": "direct_png_composite",
            "user_response_exact": "approved, whats next",
            "approval_scope": "Appearance of the displayed SSUZY1 004 direct composite v3 after the belly-contour correction only.",
            "output": image, "artifact_record": pin(HERE / "record.json"),
            "request": pin(HERE / "request.json"), "previous_selection": copy.deepcopy(state),
            "production_integrated": False, "native_motion_checked": False,
        })
    acceptance = read(acceptance_path)
    assert acceptance["output"] == image and acceptance["user_response_exact"] == "approved, whats next"
    if state.get("appearance_approval", {}).get("output") != image:
        old_approval = copy.deepcopy(state["appearance_approval"])
        state.setdefault("appearance_approval_history", []).append(old_approval)
        state.setdefault("artifact_history", []).append({
            **copy.deepcopy(state["display_artifact"]), "status": "previous_approved_selection",
            "output": old_approval["output"], "appearance_approval": old_approval,
        })
        state["comparison_previous"] = old_approval["output"]
        state["previous_label"] = "Previous approved imported drawing"
    state.update(
        review_status="approved_by_user", display_version=None,
        status_text="User approved direct composite v3 with the inward belly curve and stacked legs.",
        requested_change=artifact_record["requested_change"], display_label="Approved 004 direct composite v3",
        latest_feedback=pin(acceptance_path),
        appearance_approval={"record": pin(acceptance_path), "scope": acceptance["approval_scope"],
                             "output": image, "artifact_kind": "direct_png_composite", "version": 3},
        display_artifact={"kind": "direct_png_composite", "version": 3,
                          "title": "Approved 004 direct composite v3", "record": pin(HERE / "record.json")},
    )
    selection["selection_scope"] = (
        "004 direct composite v3 is appearance approved. 003 v3 bottle correction and 005 regenerated "
        "color candidate remain awaiting review. Earlier approvals remain attached to their exact outputs.")
    for key, value in selection["frames"].items():
        if key != KEY:
            assert value == before["frames"][key]
    save(selection_path, selection)
    print(json.dumps({"approved": KEY, "output": image, "acceptance": pin(acceptance_path),
                      "other_selections_unchanged": True, "production_integrated": False,
                      "native_motion_checked": False}))


if __name__ == "__main__":
    main()
