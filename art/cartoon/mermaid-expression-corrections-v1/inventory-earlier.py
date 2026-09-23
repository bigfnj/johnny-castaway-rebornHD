"""Inventory prior mermaid-family artwork without changing earlier selections."""
import json,hashlib
from pathlib import Path
ROOT=Path("D:/.ai-work/worktrees/johnny-cartoon-environment")
ART=ROOT/"art/cartoon"
OUT=ART/"mermaid-expression-corrections-v1"
def pin(path):
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
rows={}
for family in ("workers-and-mermaids-batch-v1","worker-visitor-mermaid-fixes-v1"):
    for row in json.loads((ART/family/"review-data.json").read_text(encoding="utf-8"))["assets"]:
        if row["resource"] in ("SBREAKUP.BMP","SMGFTWAV.BMP"):
            rows[row["key"]]=(family,row)
face_frames=set(range(11))|{13,14,15,19}
observations={
 0:"Visible right-facing face; low bent arm.",
 1:"Visible right-facing face with forward body lean.",
 2:"Visible downward right-facing face; hands remain low in front.",
 3:"Visible right-facing face and extended near arm.",
 4:"Visible right-facing face; wide spread of arms.",
 5:"Visible face looking right; one hand low at torso and another forward.",
 6:"Visible frontal/right-facing face, both hands at waterline.",
 7:"Visible left-facing face; reaching arm points down-left.",
 8:"Visible left-facing face framed by hands near the cheeks.",
 9:"Visible upturned face and raised hand; preserve chin-up direction.",
 10:"Almost fully covered face; a small closed eyelid/cheek remains visible between hands and hair. No mouth should be revealed.",
 11:"Face fully covered by hands and hair; no expression features available to edit.",
 12:"Low hair-and-arm silhouette; face hidden.",
 13:"Visible crying face between hands, with tears and raised worried brows in the old drawing. User requests cheerful reinterpretation as giggling while keeping hands in place.",
 14:"Very low left-facing head with visible eye/brow near waterline. Do not reveal a submerged mouth or torso.",
 15:"Latest fix is a very low left-facing head with visible eye/brow. Keep the hidden lower face and torso below water.",
 16:"Latest fix is the bowed back of the head; do not invent eyes on the rear view.",
 17:"Near-rear upright view; hair hides the face and expression.",
 18:"Near-rear leaning view; hair hides facial expression.",
 19:"Visible low left-facing face with extended tail behind; expression can change without changing tail or waterline.",
 20:"Face submerged/hidden; visible hair and arching tail only.",
 34:"Sandcastle/architectural prop, not a character face."
}
entries=[]
for key,(family,row) in sorted(rows.items()):
    n=int(row["frame"]); resource=row["resource"]
    is_tail=resource=="SMGFTWAV.BMP"
    edit=not is_tail and n in face_frames
    orig=ROOT/row["original_reference"]["path"]
    enlarged=ART/"workers-and-mermaids-batch-v1"/"reference/nearest8"/resource/f"{n:03}.png"
    rec=ROOT/row["generation_record"]["path"]
    recdata=json.loads(rec.read_text(encoding="utf-8"))
    prior={"status":"selected_review_drawing_no_formal_approval_record_located",
           "scope":"The selected drawing is preserved as the earlier review artifact. Its generation record has no appearance approval; saved family notes describe appearance drafts. Do not infer native integration or a new approval from this inventory.",
           "generation_record_appearance_approval":recdata.get("appearance_approval"),
           "evidence":[pin(ART/family/"review-data.json"),pin(ART/family/"selected-versions.json")]}
    entry={"key":key,"resource":resource,"frame":f"{n:03}","selected_family":family,
           "selected_version":row["version"],"selected_drawing":pin(ROOT/row["selected_raw"]["path"]),
           "original_reference":pin(orig),"enlarged_reference":pin(enlarged),
           "generation_record":pin(rec),"request":row.get("request"),
           "prior_approval":prior,"requires_expression_edit":edit,
           "disposition":"edit_expression" if edit else "retain_unchanged",
           "face_visibility":"none_tail_only" if is_tail else ("visible_or_partially_visible" if edit else "hidden_or_noncharacter"),
           "pose_observation":"Tail-only fin exposure/folding phase; no head or face." if is_tail else observations[n],
           "retained_reason":None if edit else ("No visible facial features; preserve source occlusion." if n!=34 or is_tail else "Architectural prop."),
           "source_sad_action_caution": (observations[n] if not is_tail and n in (10,11,12,13) else None),
           "latest_expression_direction":"Cheerful/playful visible expression, relaxed brows; treat covered-face gesture as giggling. Preserve hidden facial features and all pose/prop/waterline geometry." if edit else "Retain unchanged; do not expose a hidden face.",
           "production_integrated":False,"native_motion_checked":False}
    entries.append(entry)
output={"schema_version":1,"scope":"Earlier generated mermaid-family artwork outside mermaid-gifts-and-glimpses-batch-v1",
        "families_inspected":["workers-and-mermaids-batch-v1","worker-visitor-mermaid-fixes-v1"],
        "other_generated_mermaid_families_found":[],
        "current_user_scope":"All mermaid expressions, including earlier drawings. The only explicit sad exclusions are SMGIFT006 and SMGIFT007 in the newer batch; none of these earlier entries are those exceptions.",
        "counts":{"total":len(entries),"expression_edits":sum(e["requires_expression_edit"] for e in entries),"retained":sum(not e["requires_expression_edit"] for e in entries)},
        "source_action_notes":"SBREAKUP010-013 were previously interpreted as crying/sinking. Latest user direction overrides visible sadness; preserve covered faces and hand/hair placement. 011 and012 have no visible expression to edit.",
        "exclusions":[{"resource":"SBREAKUP.BMP","frames":list(range(21,34)),"reason":"Johnny drawings, not mermaid artwork; excluded from the earlier generated mermaid batch."}],
        "entries":entries}
OUT.mkdir(exist_ok=True)
(OUT/"earlier-inventory.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
print(json.dumps(output["counts"]))
