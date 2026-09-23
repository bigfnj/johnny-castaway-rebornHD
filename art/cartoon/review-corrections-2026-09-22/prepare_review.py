"""Restore the exact user-selected partial 005 v2 and seed this focused review."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ROOT = ART.parents[1]
VISITOR = ART / "visitor-leg-pose-corrections-v2"
MERMAID = ART / "mermaid-expression-corrections-v1"
QUOTE = "keep the partial 005 v2 (unless you want to take another crack at generating based on the original)."
EXPECTED = "ce4cd909762c0236e08f49b2c194e2891b3cfc538915a0682cc6dc3c28401597"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def main():
    selection_path = VISITOR / "selected-versions.json"
    selection = read(selection_path)
    before = copy.deepcopy(selection)
    state = selection["frames"]["SSUZY1.BMP-005"]
    image = pin(VISITOR / "generation/SSUZY1.BMP/005-generated-v2.png")
    assert image["sha256"] == EXPECTED
    record = read(VISITOR / "generation/SSUZY1.BMP/005-record-v2.json")
    acceptance_path = VISITOR / "acceptance/appearance-005-partial-v2-restored.json"
    if not acceptance_path.exists():
        assert state["previous_label"] == "Previous partial 005 v2"
        assert state["comparison_previous"] == image
        save(acceptance_path, {
            "schema_version": 1, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "frame": "SSUZY1.BMP-005", "version": 2, "user_response_exact": QUOTE,
            "approval_scope": "Restore and keep the exact drawing shown as Previous partial 005 v2 in the visitor review.",
            "output": image, "artifact_record": pin(VISITOR / "generation/SSUZY1.BMP/005-record-v2.json"),
            "previous_selection": copy.deepcopy(state), "production_integrated": False, "native_motion_checked": False,
        })
    acceptance = read(acceptance_path)
    assert acceptance["output"] == image and acceptance["user_response_exact"] == QUOTE
    if state.get("appearance_approval", {}).get("output") != image:
        old = copy.deepcopy(state["appearance_approval"])
        state.setdefault("appearance_approval_history", []).append(old)
        if state.get("display_artifact"):
            state.setdefault("artifact_history", []).append({**copy.deepcopy(state["display_artifact"]),
                "status": "previous_approved_selection", "output": old["output"], "appearance_approval": old})
        state["comparison_previous"] = old["output"]
        state["previous_label"] = "Prior selected imported 005"
    state.pop("display_artifact", None)
    state.update(display_version=2, display_label="Selected Previous partial 005 v2",
        review_status="approved_by_user", latest_version=2, latest_status="returned",
        status_text="The user chose the exact Previous partial 005 v2 drawing. It is restored unchanged.",
        requested_change=QUOTE, latest_feedback=pin(acceptance_path),
        appearance_approval={"record": pin(acceptance_path), "scope": acceptance["approval_scope"],
                             "output": image, "version": 2})
    selection["selection_scope"] = "004 body composite v3 remains appearance approved; its upright-bottle edit is a new pending correction. The exact Previous partial 005 v2 is restored by user request. 003 bottle and other corrections remain separate reviews."
    for key, value in selection["frames"].items():
        if key != "SSUZY1.BMP-005":
            assert value == before["frames"][key]
    save(selection_path, selection)
    current = {row["key"]: row for row in read(MERMAID / "review-data.json")["assets"]}
    scope = [
        ("SSUZY1.BMP", "004", "Hold the sunblock bottle upright instead of pointing down."),
        ("SSUZY1.BMP", "005", QUOTE),
        ("SMGIFT.BMP", "014", "Turn the extended hand palm up as if ready to receive something."),
        ("SMGIFT.BMP", "037", "Show the life preserver and rope; make the center transparent."),
        ("SMGIFT.BMP", "038", "Keep the life preserver and rope consistent across the scene."),
        ("SMGIFT.BMP", "039", "Show the life preserver with only her hand holding it; the shape is not hair."),
        ("SMGIFT.BMP", "041", "Match the life preserver and rope chosen for the adjacent scene drawings."),
        ("SMGIFT.BMP", "043", "Match the life preserver and rope chosen for the adjacent scene drawings."),
        ("SMGLIMSE.BMP", "000", "Show both eyes looking more toward the viewer."),
        ("SMGLIMSE.BMP", "010", "Face farther away from the viewer and show more of her back."),
        ("SMGLIMSE.BMP", "012", "Lean back farther as if watching something in the sky."),
        ("SMGLIMSE.BMP", "013", "Face a little farther away from the viewer."),
        ("SMGLIMSE.BMP", "014", "Look up."),
    ]
    scope_path = HERE / "review-scope.json"
    if not scope_path.exists():
        entries = []
        for resource, frame, change in scope:
            old = current[f"{resource}-{frame}"]
            entries.append({"resource": resource, "frame": frame, "original": old["images"]["original"],
                "previous": old["images"]["revised"] or old["images"]["previous"],
                "output": None, "status": "pending", "requested_change": change})
        save(scope_path, {"entries": entries})
    save(HERE / "selection005/manifest.json", {"entries": [{"resource": "SSUZY1.BMP", "frame": "005",
        "original": current["SSUZY1.BMP-005"]["images"]["original"],
        "previous": acceptance["previous_selection"]["appearance_approval"]["output"],
        "output": image, "status": "selected_by_user", "requested_change": QUOTE,
        "request": pin(acceptance_path), "record": acceptance["artifact_record"],
        "appearance_approval": state["appearance_approval"], "output_label": "Selected Previous partial 005 v2"}]})
    print(json.dumps({"restored_005": image, "acceptance": pin(acceptance_path), "other_selections_unchanged": True}))

if __name__ == "__main__":
    main()
