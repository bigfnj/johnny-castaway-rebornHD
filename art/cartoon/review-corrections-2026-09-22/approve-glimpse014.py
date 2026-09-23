"""Persist the user's explicit acceptance of the displayed Glimpse 014 v1."""
import copy
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EXPECTED="4b6db9d40db5caf30289da8f5e2448f0b0fcb3fec7c8f87e0f1f7dca5e84b956"
QUOTE="014 is good, you really cant get 13 to just turn away from the viewer slightly ?"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pin(path):
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")

def main():
    path=HERE/"glimse/manifest.json"
    manifest=read(path)
    before=copy.deepcopy(manifest)
    entry=next(row for row in manifest["entries"] if row["frame"]=="014")
    output=pin(ROOT/(entry["output"]["path"] if isinstance(entry["output"],dict) else entry["output"]))
    assert output["sha256"]==EXPECTED
    acceptance_path=HERE/"acceptance/appearance-glimpse014-v1.json"
    if not acceptance_path.exists():
        save(acceptance_path,{"schema_version":1,"recorded_at_utc":datetime.now(timezone.utc).isoformat(),
            "key":"SMGLIMSE.BMP-014","user_response_exact":QUOTE,
            "approval_scope":"Appearance of the displayed Glimpse 014 v1. The user's acceptance resolves its earlier mouth-detail review concern; 013 remains a separate requested correction.",
            "output":output,"previous_review_entry":copy.deepcopy(entry),
            "production_integrated":False,"native_motion_checked":False})
    acceptance=read(acceptance_path)
    assert acceptance["output"]==output and acceptance["user_response_exact"]==QUOTE
    approval={"record":pin(acceptance_path),"scope":acceptance["approval_scope"],"output":output}
    if entry.get("appearance_approval")!=approval:
        entry.setdefault("review_history",[]).append({"status":entry["status"],
            "visual_review":entry.get("visual_review"),"latest_attempt_request":entry.get("latest_attempt_request"),
            "latest_attempt_record":entry.get("latest_attempt_record")})
    entry.update(status="approved_by_user",appearance_approval=approval,
                 visual_review="User accepted this drawing: '014 is good'. Earlier repair requests remain linked as history.")
    for row,old in zip(manifest["entries"],before["entries"]):
        if row["frame"]!="014":
            assert row==old
    save(path,manifest)
    print(json.dumps({"approved":"SMGLIMSE.BMP-014","output":output,"acceptance":pin(acceptance_path),
                      "other_entries_unchanged":True,"013_approved":False}))

if __name__=="__main__":
    main()
