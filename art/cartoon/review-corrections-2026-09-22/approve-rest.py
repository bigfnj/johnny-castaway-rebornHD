"""Record 'the rest are approved' for the ten displayed corrections only."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
VISITOR=HERE.parent/"visitor-leg-pose-corrections-v2"
KEYS={"SSUZY1.BMP-004","SMGIFT.BMP-014","SMGIFT.BMP-037","SMGIFT.BMP-038","SMGIFT.BMP-039",
      "SMGIFT.BMP-041","SMGIFT.BMP-043","SMGLIMSE.BMP-000","SMGLIMSE.BMP-010","SMGLIMSE.BMP-012"}
EXPECTED_004="a931a3974ea04b86665b9efbaf7f6104ce7271b1fd6b255d15600d7fd6058344"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pin(path):
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

def output_pin(value):
    result=pin(ROOT/(value["path"] if isinstance(value,dict) else value))
    if isinstance(value,dict) and value.get("sha256"):
        assert result["sha256"]==value["sha256"]
    return result

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")

def main():
    rows={row["key"]:row for row in read(HERE/"review-data.json")["entries"]}
    assert rows["SSUZY1.BMP-004"]["output"]["sha256"]==EXPECTED_004
    acceptance_path=HERE/"acceptance/appearance-rest-v1.json"
    if not acceptance_path.exists():
        approved=[]
        for key in sorted(KEYS):
            row=rows[key]
            assert row["status"]=="awaiting_review",key
            approved.append({"key":key,"output":output_pin(row["output"]),
                "record":output_pin(row["record"]),"request":output_pin(row["request"]),
                "previous":output_pin(row["previous"]),"source_manifest":output_pin(row["manifest"]),
                "previous_appearance_approval":row.get("appearance_approval")})
        save(acceptance_path,{"schema_version":1,"recorded_at_utc":datetime.now(timezone.utc).isoformat(),
            "user_response_exact":"the rest are approved",
            "approval_scope":"Appearance of the ten displayed corrections listed by exact output hash. Excludes SMGLIMSE 013 and 014 retries; 005 remains the separately selected partial v2.",
            "approved":approved,"excluded":["SMGLIMSE.BMP-013","SMGLIMSE.BMP-014"],
            "production_integrated":False,"native_motion_checked":False})
    acceptance=read(acceptance_path)
    accepted={entry["key"]:entry for entry in acceptance["approved"]}
    assert set(accepted)==KEYS
    approvals={}
    for folder in ("suzy","gift014","preserver","glimse"):
        path=HERE/folder/"manifest.json"
        manifest=read(path)
        for entry in manifest["entries"]:
            key=f'{entry["resource"]}-{str(entry["frame"]).zfill(3)}'
            if key not in KEYS:
                continue
            output=output_pin(entry["output"])
            assert output==accepted[key]["output"],key
            approval={"record":pin(acceptance_path),"scope":"Appearance of this exact correction, approved with 'the rest are approved'.",
                      "output":output}
            if entry.get("appearance_approval") and entry["appearance_approval"]!=approval:
                entry.setdefault("appearance_approval_history",[]).append(copy.deepcopy(entry["appearance_approval"]))
            entry.update(status="approved_by_user",appearance_approval=approval)
            approvals[key]=approval
        save(path,manifest)
    selection_path=VISITOR/"selected-versions.json"
    selection=read(selection_path)
    before=copy.deepcopy(selection)
    state=selection["frames"]["SSUZY1.BMP-004"]
    approval=approvals["SSUZY1.BMP-004"]
    if state["appearance_approval"]["output"]!=approval["output"]:
        old=copy.deepcopy(state["appearance_approval"])
        state.setdefault("appearance_approval_history",[]).append(old)
        state.setdefault("artifact_history",[]).append({**copy.deepcopy(state["display_artifact"]),
            "status":"previous_approved_selection","output":old["output"],"appearance_approval":old})
        state["comparison_previous"]=old["output"]
        state["previous_label"]="Previously approved belly and stacked-leg drawing"
    state.update(appearance_approval={**approval,"artifact_kind":"direct_png_composite","version":1},
        display_version=None,review_status="approved_by_user",display_label="Approved 004 upright bottle",
        status_text="User approved the upright-bottle correction with the exact inward belly curve and stacked legs preserved.",
        requested_change=rows["SSUZY1.BMP-004"]["requested_change"],latest_feedback=pin(acceptance_path),
        display_artifact={"kind":"direct_png_composite","version":1,"title":"Approved 004 upright bottle",
                          "record":accepted["SSUZY1.BMP-004"]["record"]})
    selection["selection_scope"]="004 upright-bottle correction is appearance approved. The selected partial 005 v2 remains unchanged. 003 and SMGLIMSE 013/014 corrections remain separate reviews."
    for key,value in selection["frames"].items():
        if key!="SSUZY1.BMP-004":
            assert value==before["frames"][key]
    save(selection_path,selection)
    print(json.dumps({"approved_count":len(KEYS),"acceptance":pin(acceptance_path),"004_output":approval["output"],
                      "013_014_approved":False,"005_unchanged":True,"production_integrated":False,"native_motion_checked":False}))

if __name__=="__main__":
    main()
