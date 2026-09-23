"""Sync requested corrections into the current review views without approving them."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ROOT = ART.parents[1]
VISITOR = ART / "visitor-leg-pose-corrections-v2"
MERMAID = ART / "mermaid-expression-corrections-v1"

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pin(value):
    path = ROOT / value["path"]
    result = {"path": value["path"], "url": os.path.relpath(path,VISITOR).replace(os.sep,"/"),
              "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            result.update(canvas=list(image.size),bounds=list(image.convert("RGBA").getchannel("A").point(lambda a:255 if a>=8 else 0).getbbox()))
    return result

def run_builder(path):
    spec=importlib.util.spec_from_file_location(path.parent.name.replace("-","_")+"_builder",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

def main():
    entries={row["key"]:row for row in read(HERE/"review-data.json")["entries"]}
    selected=read(VISITOR/"selected-versions.json")
    data=read(VISITOR/"color-sequence.json")
    before=copy.deepcopy(data)
    for frame in ("004","005"):
        key=f"SSUZY1.BMP-{frame}"
        approval=selected["frames"][key]["appearance_approval"]
        data["sprites"][str(int(frame))]["cartoon"]=pin(approval["output"])
        entry=entries[key]
        if entry.get("output"):
            kept=entry["status"]=="selected_by_user"
            approved=kept or entry["status"]=="approved_by_user"
            data["sprites"][str(int(frame))]["candidate"]={**pin(entry["output"]),
                "request":pin(entry["request"]), "record":pin(entry["record"]),
                "version":2 if kept else 1,"artifact_kind":"user_selection" if kept else "direct-png-composite",
                "appearance_approval":approval if approved else None,
                "review_status":"approved_by_user" if approved else "awaiting_review",
                "review_label":"Selected Previous partial 005 v2" if kept else "Upright-bottle correction: appearance approved" if approved else "Upright-bottle correction: awaiting review"}
            data["sprites"][str(int(frame))]["color_pending"]=False
    data["color_correction_status"]="004 upright-bottle correction awaits review. 005 uses your selected Previous partial 005 v2."
    data["mode_comparison_note"]="Only 004 changes between its new bottle correction and its approved body drawing."
    data["selected_mode_notice"]="Showing approved selections: 004 body composite v3 and the restored partial 005 v2. The new upright-bottle edit is awaiting review."
    data["display_notes"][0]="Review mode shows the new upright-bottle correction for 004, awaiting approval. Approved mode keeps the prior body composite v3. Both modes use the restored partial 005 v2 selected by the user."
    approved_004=entries["SSUZY1.BMP-004"]["status"]=="approved_by_user"
    if approved_004:
        data["color_correction_status"]="004 upright-bottle correction is appearance approved. 005 remains your selected Previous partial 005 v2."
        data["mode_comparison_note"]="Both modes now show your selected 004 and 005 drawings."
        data["selected_mode_notice"]="Showing approved selections: 004 upright-bottle correction and the restored partial 005 v2."
        data["display_notes"][0]="The upright-bottle correction for 004 is appearance approved and selected in both modes. Both modes retain the restored partial 005 v2. Earlier 004 body and belly approvals remain preserved in history."
    for source in data["source_pins"]:
        if source["path"]== (VISITOR/"selected-versions.json").relative_to(ROOT).as_posix():
            source["sha256"]=hashlib.sha256((VISITOR/"selected-versions.json").read_bytes()).hexdigest()
    assert data["steps"]==before["steps"] and data["nominal_excerpt_ms"]==5840
    for frame,sprite in data["sprites"].items():
        if frame not in ("4","5"):
            assert sprite==before["sprites"][frame]
    template=(VISITOR/"color-sequence-template.html").read_text(encoding="utf-8")
    template=template.replace("004 approved; 005 candidate awaiting review.","Current Suzy correction review.")
    template=template.replace("004 is approved. Only 005 changes between modes.","Use the menu to compare the new correction with approved selections.")
    template=template.replace("005 still awaits appearance review.","004's upright-bottle edit awaits review; 005 is selected.")
    if approved_004:
        template=template.replace("004's upright-bottle edit awaits review; 005 is selected.","004's upright-bottle correction is approved; 005 remains selected.")
        template=template.replace("Use the menu to compare the new correction with approved selections.","Both modes show your selected 004 and 005 drawings.")
    template=template.replace("'Showing approved selections: direct composite v3 for 004 and the prior imported drawing for 005.'","(data.selected_mode_notice||'Showing approved selections.')")
    template=template.replace("(s.candidate?' pending':'')","(s.candidate&&!s.candidate.appearance_approval?' pending':'')")
    template=template.replace("candidate.artifact_kind==='direct-png-composite'?'composite':'regeneration'","({'direct-png-composite':'composite','user_selection':'selection'}[candidate.artifact_kind]||'regeneration')")
    if "review-corrections-2026-09-22/review.html" not in template:
        template=template.replace('<p id="requestLinks" class="links"></p>', '<p class="links"><a href="../review-corrections-2026-09-22/review.html">Current requested corrections</a></p><p id="requestLinks" class="links"></p>')
    (VISITOR/"color-sequence-template.html").write_text(template,encoding="utf-8")
    (VISITOR/"color-sequence.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    (VISITOR/"color-sequence-review.html").write_text(template.replace("__SEQUENCE_DATA__",json.dumps(data).replace("</","<\\/")),encoding="utf-8")
    visitor_template=VISITOR/"review-template.html"
    text=visitor_template.read_text(encoding="utf-8")
    if "review-corrections-2026-09-22/review.html" not in text:
        text=text.replace("<body>",'<body><p style="margin:20px"><a href="../review-corrections-2026-09-22/review.html">Current requested corrections, including the new 004 upright-bottle candidate</a></p>')
        visitor_template.write_text(text,encoding="utf-8")
    run_builder(VISITOR/"build_review.py")
    run_builder(MERMAID/"build_review.py")
    print(json.dumps({"004_new_candidate_approved":approved_004,"005_restored_partial_v2":True,"sequence_steps":len(data["steps"]),"other_animation_frames_unchanged":True}))

if __name__=="__main__":
    main()
