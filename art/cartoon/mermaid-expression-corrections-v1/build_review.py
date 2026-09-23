"""Build the expression comparison with the user's restored SBREAKUP selection."""
import argparse
import hashlib
import html
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = HERE.parent
PRIOR = ART / "mermaid-gifts-and-glimpses-batch-v1"
VISITOR = ART / "visitor-leg-pose-corrections-v2"
RETAIN_GIFT = {6, 7, 25, 39, 40, 41, 43, 45, 46}
RETAIN_GLIMPSE = {2, 7, 9, 15, 22}
GESTURE_PASS = {f"SMGIFT.BMP-{n:03}" for n in (13, 14, 18, 20, 21, 22)} | {f"SMGLIMSE.BMP-{n:03}" for n in (12, 13, 14)} | {f"SMGFTWAV.BMP-{n:03}" for n in (3, 7)}

NOTES = {
    "SMGIFT.BMP-002": "Happy bashful giggle; open near hand partly covers the face.",
    "SMGIFT.BMP-003": "Giggling expression; raised far hand faces palm up with a natural wrist.",
    "SMGIFT.BMP-008": "Happy smile; outer hand shows its inner palm with natural thumb and fingers.",
    "SMGIFT.BMP-012": "Happy, relaxed expression while casually explaining; preserve the existing pose.",
    "SMGIFT.BMP-013": "Visible index finger curls toward herself in a friendly come-here beckon.",
    "SMGIFT.BMP-014": "Fully emerged hand faces palm upward in a come-here gesture.",
    "SMGIFT.BMP-016": "Playful happy giggle; turn the face enough to show both eyes while retaining the body.",
    "SMGIFT.BMP-017": "Playful happy giggle; turn the face enough to show both eyes while retaining the body.",
    "SMGIFT.BMP-018": "Both hands emerge from the water to cover a laugh; preserve both eyes.",
    "SMGIFT.BMP-020": "The hand emerging from the water points at herself.",
    "SMGIFT.BMP-021": "Index finger rests at the lips in a coy, playful expression.",
    "SMGIFT.BMP-022": "Preserve the happy face; rebuild both connected arms, bend the front elbow, and shape the other hand into a backward C with thumb and fingers.",
    "SMGIFT.BMP-023": "Laughing face; clasped hands keep distinct wrists and forearms.",
    "SMGIFT.BMP-024": "Smiling downward face; preserve clasped hands and separate forearms.",
    "SMGIFT.BMP-026": "Look upward with a happy excited smile; preserve both lei grips.",
    "SMGIFT.BMP-027": "Happy face; two visible hands display the lei with distinct upper and lower grips.",
    "SMGIFT.BMP-029": "Happy upward smile with both eyes visible; preserve the hand-to-forearm gesture.",
    "SMGIFT.BMP-035": "Happy face; move the near arm in front, with connected hand below the swimsuit top at the water.",
    "SMGLIMSE.BMP-000": "Make the visible eye, brow and cheek playful; keep the mouth hidden by water.",
    "SMGLIMSE.BMP-004": "Raise the smiling face above water and turn slightly toward the viewer so both eyes show.",
    "SMGLIMSE.BMP-005": "Happy low swimming pose with both eyes visible; preserve submerged anatomy.",
    "SMGLIMSE.BMP-011": "Light giggling smile; retain the hanging arm and lower splash without extra green points.",
    "SMGLIMSE.BMP-012": "Relaxed happy smile with a slight backward rest against the water; both swimsuit straps remain in place.",
    "SMGLIMSE.BMP-013": "Missing sprite: smile while looking straight up at the sky; preserve compact head and separate splash.",
    "SMGLIMSE.BMP-014": "Float on her back with face and eyes angled skyward, happy smile; preserve the separate emerging hand.",
    "SMGLIMSE.BMP-016": "Front hair falls across the eyes; coy amused smile with the bowed swimming pose.",
    "SMGLIMSE.BMP-017": "Playful giggle while leaning toward the raised hand; retain the water droplet and ripples.",
    "SMGLIMSE.BMP-018": "Happy giggle; preserve the near hand beside the face and upright pose.",
    "SMGLIMSE.BMP-019": "Huddle forward laughing with both hands at the face and two connected arms.",
    "SMGLIMSE.BMP-020": "Open happy smile during the backward diving arch; retain the entire diving pose.",
    "SMGLIMSE.BMP-021": "Delighted smile during the upside-down dive; preserve the head angle and connected tail.",
    "SMGFTWAV.BMP-003": "The green surface is the underside of the fins descending into the ocean; preserve the original phase and waterline.",
    "SMGFTWAV.BMP-007": "Show the green undersides of the fins entering the water with the original orientation.",
    "SSUZY1.BMP-004": "Match approved character colors and clean contours; preserve the selected compact torso, overlapping legs and lotion pose.",
    "SSUZY1.BMP-005": "Match approved character colors and clean contours; preserve the supporting elbow, lotion pose and removed accidental red dot.",
}
STATUS_LABELS = {
    "approved_by_user": "Appearance approved by user",
    "revised": "Revised candidate ready for review",
    "revised_unrecorded": "Image returned; record pending",
    "retained": "Retained unchanged",
    "blocked": "Blocked; no revised image returned",
    "no_image_uncertain": "No revised image; failure attribution uncertain",
    "failed": "No revised image returned",
    "revision_failed": "Latest correction blocked; previous candidate still needs this change",
    "pending": "Revision pending",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")


def pin(path):
    if not path or not path.is_file():
        return None
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "url": url(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    if path.suffix.lower() == ".png":
        with Image.open(path) as im:
            alpha = im.convert("RGBA").getchannel("A")
            bounds = alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()
            result.update(canvas=list(im.size), mode=im.mode,
                          alpha_range=list(alpha.getextrema()),
                          alpha8_bounds=list(bounds) if bounds else None)
    return result


def from_pin(value):
    return ROOT / value["path"] if value and value.get("path") else None


def make_sources():
    sources = []
    before = {r["key"]: r for r in read_json(HERE / "review-data-before-gesture-pass.json")["assets"]}
    for old in read_json(PRIOR / "review-data.json")["assets"]:
        resource, frame = old["resource"], old["frame"]
        n = int(frame)
        retained = n in (RETAIN_GIFT if resource == "SMGIFT.BMP" else RETAIN_GLIMPSE)
        reason = ("Intentional sad expression: explicitly retained by the user."
                  if resource == "SMGIFT.BMP" and n in {6, 7}
                  else "No visible facial expression to change; preserve covered, submerged or non-character artwork.")
        sources.append({
            "key": old["key"], "resource": resource, "frame": frame,
            "source_family": PRIOR.name,
            "original_path": from_pin(old.get("original_reference")),
            "previous_path": from_pin(old.get("selected_raw")),
            "previous_request": from_pin(old.get("request")),
            "previous_record": from_pin(old.get("generation_record")),
            "previous_failure": from_pin(old.get("failure")),
            "retained": retained, "retained_reason": reason if retained else None,
            "prior_approval": None,
        })
        if old["key"] in GESTURE_PASS:
            snapshot = before[old["key"]]
            if snapshot["images"]["revised"]:
                sources[-1]["previous_path"] = from_pin(snapshot["images"]["revised"])
                sources[-1]["previous_request"] = from_pin(snapshot["request"])
                sources[-1]["previous_record"] = from_pin(snapshot["generation_record"])
    for old in read_json(HERE / "earlier-inventory.json")["entries"]:
        sources.append({
            "key": old["key"], "resource": old["resource"], "frame": old["frame"],
            "source_family": old["selected_family"],
            "original_path": from_pin(old.get("original_reference")),
            "previous_path": from_pin(old.get("selected_drawing")),
            "previous_request": from_pin(old.get("request")),
            "previous_record": from_pin(old.get("generation_record")),
            "previous_failure": None,
            "retained": old["resource"] == "SBREAKUP.BMP" or (old["disposition"] == "retain_unchanged" and old["key"] not in GESTURE_PASS),
            "retained_reason": "Previous drawing restored by user request; preserve this series' sad expressions and original action." if old["resource"] == "SBREAKUP.BMP" else old.get("retained_reason") if old["key"] not in GESTURE_PASS else None,
            "prior_approval": old.get("prior_approval"),
        })
    visitor_rows = {row["frame"]: row for row in read_json(VISITOR / "review-data.json")["frames"]}
    for frame in ("004", "005"):
        old = visitor_rows[frame]
        record = "transparent-record.json" if frame == "004" else "record.json"
        previous_path = VISITOR / f"imported-{frame}-v1/{frame}-transparent-v1.png"
        previous_approval = old.get("appearance_approval")
        if previous_approval and previous_approval["output"]["path"] != previous_path.relative_to(ROOT).as_posix():
            previous_approval = next((approval for approval in old.get("appearance_approval_history", [])
                                      if approval["output"]["path"] == previous_path.relative_to(ROOT).as_posix()), None)
        sources.append({
            "key": f"SSUZY1.BMP-{frame}", "resource": "SSUZY1.BMP", "frame": frame,
            "source_family": VISITOR.name,
            "original_path": from_pin(old["original"]),
            "previous_path": previous_path,
            "previous_request": None,
            "previous_record": VISITOR / f"imported-{frame}-v1/{record}",
            "previous_failure": None, "retained": False, "retained_reason": None,
            "prior_approval": previous_approval,
        })
    assert len(sources) == 103 and len({r["key"] for r in sources}) == 103
    return sources


def frame_versions(folder, frame):
    versions = {}
    for path in folder.glob(f"{frame}-*"):
        match = re.match(rf"{frame}-(?:generated-v(\d+)\.png|record-v(\d+)\.json|v(\d+)-(request|failure)\.json)$", path.name)
        if not match:
            continue
        version = int(next(x for x in match.groups()[:3] if x is not None))
        kind = "output" if match[1] else "record" if match[2] else match[4]
        versions.setdefault(version, {})[kind] = path
    return versions


def load_direct_composite_004(record_path):
    """Read an explicitly requested composite without changing approved selectors."""
    record_path = Path(record_path).resolve()
    record = read_json(record_path)
    assert record["resource"] == "SSUZY1.BMP" and str(record["frame"]).zfill(3) == "004"
    assert record["mode"] in ("direct-png-composite", "built-in-imagegen-with-local-composite")
    assert record.get("appearance_approval") is None
    assert record.get("production_integrated") is False
    assert record.get("native_motion_checked") is False
    output = pin(ROOT / record["output"]["path"])
    request = pin(ROOT / record["request"]["path"])
    assert output and output["sha256"] == record["output"]["sha256"]
    assert request and request["sha256"] == record["request"]["sha256"]
    selection = read_json(VISITOR / "selected-versions.json")["frames"]["SSUZY1.BMP-004"]
    approval = selection.get("appearance_approval")
    if approval and approval["output"] == record["output"]:
        approval_record = pin(ROOT / approval["record"]["path"])
        assert approval_record and approval_record["sha256"] == approval["record"]["sha256"]
        acceptance = read_json(ROOT / approval["record"]["path"])
        accepted_output = acceptance.get("output") or next(entry["output"] for entry in acceptance["approved"] if entry["key"] == "SSUZY1.BMP-004")
        assert accepted_output == record["output"]
    else:
        approval = None
    return {"version": record.get("version", selection.get("display_artifact", {}).get("version", 2)), "output": output,
            "record": pin(record_path), "request": request,
            "artifact_kind": "direct-png-composite", "correction": record.get("requested_change", selection.get("requested_change")), "failure": None,
            "failure_details": None, "appearance_approval": approval}


def build_row(source, direct_composite_004=None):
    resource, frame = source["resource"], source["frame"]
    versions = frame_versions(HERE / "generation" / resource, frame)
    returned = [v for v, files in versions.items() if "output" in files]
    selected = max(returned) if returned and not source["retained"] else None
    latest = max(versions) if versions else None
    latest_files = versions.get(latest, {})
    latest_failure = read_json(latest_files["failure"]) if "failure" in latest_files else None
    if source["key"] in GESTURE_PASS and latest_failure and selected is not None and latest > selected:
        selected = None
    if source["retained"]:
        status = "retained"
    elif selected is not None:
        status = "revised" if "record" in versions[selected] else "revised_unrecorded"
    elif latest_failure:
        if returned:
            status = "revision_failed"
        elif latest_failure.get("attribution"):
            status = "no_image_uncertain"
        elif latest_failure.get("status") == "blocked" or "moderation_blocked" in latest_failure.get("error", ""):
            status = "blocked"
        else:
            status = "failed"
    else:
        status = "pending"
    selected_files = versions.get(selected, {})
    images = {
        "original": pin(source["original_path"]),
        "previous": pin(source["previous_path"]),
        "revised": pin(selected_files.get("output")),
    }
    correction = source["retained_reason"] if source["retained"] else NOTES.get(
        source["key"], "Cheerful, playful visible expression with relaxed brows and lifted cheeks; preserve pose, clothing, occlusions and waterline.")
    attempts = []
    for version, files in sorted(versions.items()):
        failure = read_json(files["failure"]) if "failure" in files else None
        attempts.append({
            "version": version,
            "request": pin(files.get("request")), "record": pin(files.get("record")),
            "output": pin(files.get("output")), "failure": pin(files.get("failure")),
            "failure_details": failure,
        })
    status_text = STATUS_LABELS[status]
    if selected is not None:
        status_text += f" (v{selected})"
    if selected is not None and latest != selected and latest_failure:
        status_text += f"; later v{latest} returned no image"
    if resource == "SSUZY1.BMP" and selected is None:
        status_text += ". The selected transparent cutout remains in Previous."
    row = {
        "key": source["key"], "resource": resource, "frame": frame, "in_gesture_pass": source["key"] in GESTURE_PASS,
        "source_family": source["source_family"], "status": status, "status_text": status_text,
        "correction": correction, "retained_reason": source["retained_reason"],
        "selected_version": selected, "latest_attempt_version": latest,
        "images": images, "attempts": attempts,
        "selection_decision": {"source": "user", "action": "restore_previous", "drawing": images["previous"], "reason": "SBREAKUP is intended to be sad; keep previous drawings."} if resource == "SBREAKUP.BMP" else None,
        "request": pin(latest_files.get("request")),
        "generation_record": pin(selected_files.get("record")),
        "failure": pin(latest_files.get("failure")),
        "failure_attribution": latest_failure.get("attribution") if latest_failure and not source["retained"] else None,
        "previous_request": pin(source["previous_request"]),
        "previous_record": pin(source["previous_record"]),
        "previous_failure": pin(source["previous_failure"]),
        "prior_approval": source["prior_approval"],
        "appearance_approval": None, "production_integrated": False, "native_motion_checked": False,
    }
    if source["key"] == "SSUZY1.BMP-004" and direct_composite_004:
        composite = direct_composite_004
        row["images"]["revised"] = composite["output"]
        row.update(
            status="revised",
            status_text=f'Direct composite v{composite["version"]}: awaiting appearance review',
            correction=composite.get("correction") or "Place the legs over one another as in the original, preserving natural human proportions and the sunscreen pose.",
            selected_version=None, candidate_version=composite["version"],
            latest_attempt_version=composite["version"], latest_attempt_kind="direct-png-composite",
            candidate_kind="direct-png-composite", request=composite["request"],
            generation_record=None, candidate_record=composite["record"],
            failure=None, failure_attribution=None,
        )
        row["attempts"].append(composite)
        if composite.get("appearance_approval"):
            row.update(status="approved_by_user",
                       status_text=f'Direct composite v{composite["version"]}: appearance approved by user',
                       appearance_approval=composite["appearance_approval"])
    return row


def link(info, label):
    if not info:
        return ""
    return f'<a href="{html.escape(info["url"], quote=True)}" target="_blank" rel="noopener">{html.escape(label)}</a>'


def apply_focused_review(rows):
    focused_path = ART / "review-corrections-2026-09-22/review-data.json"
    if not focused_path.exists():
        return rows
    entries = {entry["key"]: entry for entry in read_json(focused_path)["entries"]}
    selected = read_json(VISITOR / "selected-versions.json")["frames"]
    for row in rows:
        entry = entries.get(row["key"])
        if not entry:
            continue
        output = pin(from_pin(entry.get("output")))
        kept = entry["status"] == "selected_by_user"
        approved = kept or entry["status"] == "approved_by_user"
        row["images"].update(original=pin(from_pin(entry.get("original"))),
                             previous=pin(from_pin(entry.get("previous"))), revised=output)
        row.update(correction=entry["requested_change"], retained_reason=None,
                   status="approved_by_user" if approved else "revised" if output else "failed" if entry["status"] in ("no_image", "failed", "blocked") else "pending",
                   status_text="Previous partial 005 v2 selected by user" if kept else "Appearance approved by user" if approved else "New correction: awaiting appearance review" if output else "Requested correction has no new image yet",
                   appearance_approval=entry.get("appearance_approval") if approved else None,
                   request=pin(from_pin(entry.get("request"))),
                   candidate_record=pin(from_pin(entry.get("record"))), generation_record=None,
                   candidate_kind="user_selection" if kept else "focused_correction",
                   selected_version=2 if kept else None, latest_attempt_version=None,
                   failure=None, failure_attribution=None,
                   focused_review=pin(focused_path))
        if row["key"] in selected:
            state = selected[row["key"]]
            previous = row["images"]["previous"]
            approvals = [state.get("appearance_approval")] + state.get("appearance_approval_history", [])
            matched = next((approval for approval in approvals if approval and previous and approval["output"]["sha256"] == previous["sha256"]), None)
            if matched:
                row["prior_approval"] = matched
        if kept:
            row["selection_decision"] = {"source": "user", "action": "restore_previous", "drawing": output,
                                         "reason": entry["requested_change"]}
        elif approved:
            row["selection_decision"] = {"source": "user", "action": "approve_current", "drawing": output,
                                         "approval": entry["appearance_approval"]}
        if entry["status"] == "needs_correction":
            row.update(status="revision_failed", status_text="Incomplete draft: mouth detail missing; repair returned no image",
                       failure=pin(from_pin(entry.get("latest_attempt_record"))))
    return rows


def render_card(row):
    key = row["key"]
    panels = []
    for kind, label in [("original", "Original"), ("previous", "Previous drawing"), ("revised", "Revised candidate")]:
        if kind == "revised" and row.get("candidate_kind") == "direct-png-composite":
            label = "Approved direct composite" if row.get("appearance_approval") else "Direct composite candidate"
        info = row["images"][kind]
        if info:
            display = (f'<a class="art" href="{html.escape(info["url"], quote=True)}" target="_blank" rel="noopener" aria-label="Open {kind} {key}">'
                       f'<canvas width="1000" height="650" data-key="{key}" data-kind="{kind}" aria-label="{kind} {key}"></canvas></a>')
        else:
            message = ("Retained unchanged. See Previous drawing." if kind == "revised" and row["status"] == "retained"
                       else row["status_text"] if kind == "revised"
                       else "No previous drawing was returned." if kind == "previous"
                       else "Original unavailable.")
            display = f'<div class="empty">{html.escape(message)}</div>'
        panels.append(f'<div class="panel"><h3>{label}</h3>{display}</div>')
    links = [link(row.get(field), label) for field, label in [
        ("request", "Exact latest request"), ("generation_record", "Candidate record"),
        ("candidate_record", "Composite record"),
        ("failure", "Recorded failure"), ("previous_record", "Previous record")]]
    links = [v for v in links if v]
    history = []
    for attempt in row["attempts"]:
        parts = [link(attempt.get(kind), kind.title()) for kind in ["request", "output", "record", "failure"]]
        prefix = "Direct composite " if attempt.get("artifact_kind") == "direct-png-composite" else ""
        history.append(f'<li>{prefix}v{attempt["version"]}: {" &middot; ".join(p for p in parts if p)}</li>')
    if row["previous_request"] or row["previous_failure"]:
        history.append('<li>Previous: ' + " &middot; ".join(x for x in [
            link(row["previous_request"], "Request"), link(row["previous_failure"], "Failure")] if x) + '</li>')
    attribution = (f'<p class="failure-note">{html.escape(row["failure_attribution"])}</p>'
                   if row["failure_attribution"] else "")
    if key == "SMGFTWAV.BMP-003":
        attribution += '<p class="failure-note">Geometry still needs review: the new underside forms a broad arch with two water contacts. Compare that fold with the original.</p>'
    history_html = '<details><summary>Request and output history</summary><ul>' + "".join(history) + '</ul></details>' if history else ""
    return (f'<article id="frame-{key}" data-resource="{row["resource"]}" data-frame="{row["frame"]}" data-status="{row["status"]}" data-pass="{str(row["in_gesture_pass"]).lower()}">'
            f'<h2>{html.escape(row["resource"].removesuffix(".BMP"))} {row["frame"]}</h2>'
            f'<p class="state {row["status"]}">{html.escape(row["status_text"])}</p>'
            f'<p class="correction">{html.escape(row["correction"])}</p>{attribution}'
            '<div class="panels">' + "".join(panels) + '</div>'
            f'<p class="links">{" &middot; ".join(links)}</p>{history_html}</article>')


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mermaid expression and visitor finish review</title>
<style>
:root{color-scheme:dark;--bg:#142730;--card:#223f4d;--text:#f2f7fa;--muted:#c2dce6;--accent:#78daf0;--check1:#f4f1e8;--check2:#e2ded3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,sans-serif}
header,main,footer{max-width:1740px;margin:auto;padding:22px 28px}h1{font-size:28px;margin:0 0 10px}h2{font-size:20px;margin:0}h3{font-size:15px;margin:0 0 8px}
p{margin:10px 0}a{color:#a9e8ff;text-underline-offset:3px}.scope{max-width:1050px;color:var(--muted)}.toolbar{position:sticky;top:0;z-index:10;background:#142730f5;border-block:1px solid #496774;padding:13px 28px;display:flex;flex-wrap:wrap;gap:12px;align-items:end}
label{font-size:13px;display:grid;gap:4px}input,select,button{font:inherit;color:var(--text);background:#233f4d;border:1px solid #658793;border-radius:5px;padding:7px 10px}input{width:160px}button{cursor:pointer}button:hover{background:#355b6c}
#visible-count{align-self:center;color:var(--muted);margin-left:auto}article{background:var(--card);border-radius:12px;padding:20px;margin-bottom:20px;scroll-margin-top:130px}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:20px}.panel{min-width:0}
.art,.empty{display:block;width:100%;aspect-ratio:1000/650;border-radius:4px;overflow:hidden}.art{background-color:var(--check1);background-image:linear-gradient(45deg,var(--check2) 25%,transparent 25%),linear-gradient(-45deg,var(--check2) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--check2) 75%),linear-gradient(-45deg,transparent 75%,var(--check2) 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}
canvas{display:block;width:100%;height:100%}.empty{display:grid;place-items:center;text-align:center;padding:22px;border:1px dashed #79929c;color:var(--muted);background:#19323e}.state{font-weight:650}.revised{color:#9ee8b0}.retained{color:#bdd9ef}.blocked,.failed,.no_image_uncertain{color:#ffd089}.pending,.revised_unrecorded{color:#e5de9b}
.correction{color:#e6f2f7}.links,details{font-size:13px}.failure-note,.load-error,.revision_failed{color:#ffcf95;max-width:1200px}details{margin-top:10px}body.dark-checker{--check1:#34444e;--check2:#25343d}[hidden]{display:none!important}#loading{font-size:13px;color:var(--muted)}nav{display:flex;gap:14px;flex-wrap:wrap;font-size:14px}footer{color:var(--muted);font-size:13px}.pass-toggle{display:flex;align-items:center;align-self:center}.pass-toggle input{width:auto}
@media(max-width:800px){header,main,footer{padding:16px}.toolbar{padding:12px}.panels{grid-template-columns:1fr}.art,.empty{max-height:480px}#visible-count{margin:0}h1{font-size:24px}}
</style>
</head>
<body>
<header>
<h1>Mermaid expressions and visitor finish</h1>
<p>{{SUMMARY}}</p>
<p class="scope">Compare original art, the previous selected drawing, and each returned revision. SMGIFT and SMGLIMSE expressions are happy and playful except the intentionally sad SMGIFT 006 and 007. All SBREAKUP entries now use the previous drawings, preserving that story's sad expressions as requested. New gesture and fin corrections await appearance review.</p>
<nav>{{NAV}}</nav>
<p class="links">{{NOTES}}</p>
<p id="loading">Preparing image panels...</p>
</header>
<div class="toolbar">
<label>Resource<select id="resource"><option value="">All resources</option>{{RESOURCES}}</select></label>
<label>Frame<input id="frame" inputmode="numeric" placeholder="e.g. 004 or 12"></label>
<label>Status<select id="status"><option value="">All statuses</option>{{STATUSES}}</select></label>
<button id="clear" type="button">Clear filters</button>
<button id="checker" type="button" aria-pressed="false">Use dark checkerboard</button>
<label class="pass-toggle"><input id="pass-only" type="checkbox">This gesture and fin pass only</label>
<span id="visible-count"></span>
</div>
<main>{{CARDS}}</main>
<footer>Image files are preserved as returned or previously selected. Display panels fit visible alpha bounds for comparison; click any image to open its full file. <a href="review-data.json">Review data</a></footer>
<script id="review-data" type="application/json">{{DATA}}</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("review-data").textContent);
const cards=[...document.querySelectorAll("article")];
const resource=document.getElementById("resource"),frame=document.getElementById("frame"),status=document.getElementById("status");
const passOnly=document.getElementById("pass-only");
function filter(){
  const raw=frame.value.trim().toLowerCase(), query=/^\d+$/.test(raw)?raw.padStart(3,"0"):raw;
  let visible=0;
  for(const card of cards){
    card.hidden=Boolean((passOnly.checked&&card.dataset.pass!=="true")||(resource.value&&card.dataset.resource!==resource.value)||(status.value&&card.dataset.status!==status.value)||(query&&!card.dataset.frame.includes(query)));
    if(!card.hidden)visible++;
  }
  document.getElementById("visible-count").textContent=visible+" / "+cards.length+" frames";
}
for(const control of [resource,frame,status,passOnly])control.addEventListener("input",filter);
document.getElementById("clear").addEventListener("click",()=>{resource.value=frame.value=status.value="";passOnly.checked=false;filter();});
document.getElementById("checker").addEventListener("click",event=>{
  const dark=document.body.classList.toggle("dark-checker");event.target.setAttribute("aria-pressed",String(dark));event.target.textContent=dark?"Use light checkerboard":"Use dark checkerboard";
});
document.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>{resource.value=a.dataset.resource;frame.value=status.value="";passOnly.checked=false;filter();}));
filter();
let loaded=0,errors=0;
const loading=document.getElementById("loading");
const tasks=data.assets.flatMap(row=>Object.entries(row.images).filter(([,info])=>info).map(([kind,info])=>({row,kind,info})));
async function worker(){
  while(tasks.length){
    const {row,kind,info}=tasks.shift();
    const canvas=document.querySelector('canvas[data-key="'+row.key+'"][data-kind="'+kind+'"]');
    try{
      const image=new Image();image.src=info.url+"?sha="+info.sha256;await image.decode();
      const b=info.alpha8_bounds||[0,0,image.width,image.height], w=b[2]-b[0],h=b[3]-b[1],scale=Math.min((canvas.width-44)/w,(canvas.height-44)/h);
      const ctx=canvas.getContext("2d");ctx.imageSmoothingEnabled=kind!=="original";
      ctx.drawImage(image,(canvas.width-w*scale)/2-b[0]*scale,(canvas.height-h*scale)/2-b[1]*scale,image.width*scale,image.height*scale);
      canvas.dataset.loaded="true";loaded++;
    }catch(error){
      errors++;canvas.dataset.loaded="false";const p=document.createElement("p");p.className="load-error";p.textContent="Could not load "+kind+" "+row.key+": "+error.message;canvas.parentElement.after(p);
    }
    loading.textContent=loaded+" image panels loaded"+(errors?"; "+errors+" could not load.":".");
  }
}
Promise.all(Array.from({length:6},worker)).then(()=>{loading.dataset.complete="true";loading.textContent=loaded+" image panels loaded"+(errors?"; "+errors+" could not load.":", no load errors.");});
</script>
</body></html>
"""


def main(direct_composite_004=None):
    if direct_composite_004 is None:
        selected_004 = read_json(VISITOR / "selected-versions.json")["frames"]["SSUZY1.BMP-004"]
        artifact = selected_004.get("display_artifact", {})
        if artifact.get("kind") == "direct_png_composite":
            direct_composite_004 = ROOT / artifact["record"]["path"]
    composite = load_direct_composite_004(direct_composite_004) if direct_composite_004 else None
    rows = apply_focused_review([build_row(s, composite) for s in make_sources()])
    counts = dict(Counter(r["status"] for r in rows))
    qa_flags = []
    for row in rows:
        for kind, info in row["images"].items():
            if kind == "original" and not info:
                qa_flags.append(f'{row["key"]}: original reference unavailable')
        if row["status"] == "revised_unrecorded":
            qa_flags.append(f'{row["key"]}: candidate record pending')
        if row["failure_attribution"]:
            qa_flags.append(f'{row["key"]}: concurrent failure cannot be attributed to this individual frame')
    summary = (f'{len(rows)} frames: {counts.get("approved_by_user", 0)} appearance approved, {counts.get("revised", 0)} revised candidates, '
               f'{counts.get("retained", 0)} retained, {counts.get("blocked", 0)} blocked, '
               f'{counts.get("revision_failed", 0)} later corrections blocked, '
               f'{counts.get("no_image_uncertain", 0)} without an image after an uncertain group failure, '
               f'{counts.get("pending", 0)} pending.')
    data = {
        "schema_version": 1, "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "total": len(rows), "counts": counts, "summary": summary,
        "appearance_approval": None, "production_integrated": False, "native_motion_checked": False,
        "source_inventories": [pin(PRIOR / "review-data.json"), pin(HERE / "earlier-inventory.json"), pin(VISITOR / "review-data.json")],
        "qa_flags": qa_flags, "assets": rows,
    }
    (HERE / "review-data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    resources = list(dict.fromkeys(r["resource"] for r in rows))
    nav = "".join(f'<a href="#frame-{r["key"]}" data-resource="{r["resource"]}">{r["resource"].removesuffix(".BMP")}</a>'
                  for r in [next(row for row in rows if row["resource"] == resource) for resource in resources])
    page = PAGE.replace("{{SUMMARY}}", html.escape(summary)).replace("{{NAV}}", nav)
    note_links = [link(pin(HERE / name), label) for name, label in [
        ("pass-notes.md", "Initial pass notes"),
        ("ssuzy-color-regeneration-v2.md", "New SSUZY color candidates"),
        ("gesture-and-fin-pass.md", "Latest gesture and fin notes"),
        ("smgftwav-fin-notes.md", "Fin review notes"),
        ("gesture-pass-audit.md", "Gesture pass file audit"),
        ("smglimse-notes.md", "Glimpse notes"),
        ("smgift-000-021-notes.md", "Gift 000-021 notes"),
        ("smgift-022-046-notes.md", "Gift 022-046 notes"),
        ("earlier-expression-notes.md", "Earlier pass history"),
        ("qa-audit.md", "Initial file audit"),
    ]]
    note_links.append(link(pin(VISITOR / "color-sequence-review.html"), "SSUZY color playback"))
    note_links.insert(0, link(pin(ART / "review-corrections-2026-09-22/review.html"), "Current requested corrections"))
    page = page.replace("{{NOTES}}", " &middot; ".join(v for v in note_links if v))
    page = page.replace("{{RESOURCES}}", "".join(f'<option value="{r}">{r.removesuffix(".BMP")}</option>' for r in resources))
    page = page.replace("{{STATUSES}}", "".join(f'<option value="{k}">{html.escape(STATUS_LABELS[k])} ({counts[k]})</option>' for k in STATUS_LABELS if counts.get(k)))
    page = page.replace("{{CARDS}}", "\n".join(render_card(row) for row in rows))
    page = page.replace("{{DATA}}", json.dumps(data).replace("</", "<\\/"))
    (HERE / "review.html").write_text(page, encoding="utf-8")
    print(json.dumps({"total": len(rows), "counts": counts, "image_panels": sum(bool(i) for row in rows for i in row["images"].values()), "qa_flags": qa_flags}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-composite-004", type=Path,
                        help="Use this direct-composite record for the pending SSUZY1 004 candidate.")
    main(parser.parse_args().direct_composite_004)
