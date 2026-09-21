"""Build an original-only context workup. No generated images are included."""
import hashlib
import io
import json
import shutil
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = HERE.parent / "workers-and-mermaids-batch-v1"
INV = HERE.parent / "character-inventory-v1"
GROUPS = {"SSUZY1.BMP": list(range(12)), "SBREAKUP.BMP": list(range(12, 19))}

def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def state(resource, frame):
    if resource == "SSUZY1.BMP":
        if frame == 0:
            return "recovered", "Blocked, then recovered", "The first attempt returned no image. A second attempt produced a draft. The whole family was later deferred."
        if frame == 1:
            return "success", "Draft returned", "A draft was produced on the first attempt. This neighboring frame was not blocked."
        if frame == 2:
            return "blocked", "No output after two attempts", "Both saved attempts returned no image. The first has an individual failure record; the second is recorded in the family status log."
        if frame == 3:
            return "blocked", "No output recorded", "The saved first attempt returned no image according to the family status log. No separate per-call failure record was saved."
        if frame == 11:
            return "success", "Bottle drafts returned", "Both bottle attempts produced drafts. This standalone prop was not blocked."
        return "not-run", "Deferred before running", "A request was saved, but it was never sent. This frame is shown for sequence context and must not be called blocked."
    if frame in (15, 16):
        return "recovered", "Pair recovered on retry", "The parallel 015/016 attempt reported an output block without identifying which frame failed. Neither raw returned. Separate second attempts produced both drafts."
    return "context", "Neighboring frame", "A draft was produced for this neighboring pose. It provides context for the recovered 015/016 pair."

DESCRIPTIONS = {
"SSUZY1.BMP": {
0: "Low side recline, head at left, hands over a small flat reading item.",
1: "Raised forearm and tiny cap; the separate oil bottle stands at far left.",
2: "Reaching down-left toward the bottle, with both legs extending right.",
3: "Turning toward the viewer; bottle partly hidden between the hands.",
4: "More frontal recline, hands and bottle low in front, one knee raised.",
5: "Propped transition toward sitting, with overlapping bent legs.",
6: "Upright recline, bottle raised at left and the other hand near the knee.",
7: "Seated front, one leg folded low and the other knee raised.",
8: "Hand near the separate bottle; other hand on the raised knee.",
9: "Applying oil to the raised shin; no separate bottle in this sprite.",
10: "Leaning farther toward the shin and ankle at image-right.",
11: "The separate tanning-oil bottle."
},
"SBREAKUP.BMP": {
12: "A low, partly submerged head-and-hair pose with a small arm portion.",
13: "Hands to face, upper body raised, long hair trailing right.",
14: "Face at the left waterline, hair lying along the surface.",
15: "Lower surface pose, with the face at left and hair extending right.",
16: "Back of the bowed head, turquoise band, hair sloping down-right.",
17: "Upright near-rear view, with hair covering most of the torso.",
18: "Forward-leaning near-rear view, hair trailing diagonally right."
}}

def main():
    import zipfile
    index_path = INV / "source/frame-index.json"
    mapping_path = INV / "scene-map/resource-map.json"
    archive_path = INV / "reference-originals.zip"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    lookup = {(r["resource"], r["frame"]): r for r in index["frames"]}
    resources = {r["resource"]: r for r in mapping["resources"]}
    rows = []
    evidence_paths = [
        PRIOR / "deferred/SSUZY1-status.json",
        PRIOR / "generation/SSUZY1.BMP/000-v1-failure.json",
        PRIOR / "generation/SSUZY1.BMP/002-v1-failure.json",
        PRIOR / "generation/SBREAKUP.BMP/015-v1-attempt.json",
        PRIOR / "generation/SBREAKUP.BMP/016-v1-attempt.json",
        PRIOR / "visitor-source-notes.md",
        PRIOR / "mermaid-source-notes.md",
    ]
    with zipfile.ZipFile(archive_path) as archive:
        for resource, frames in GROUPS.items():
            for frame in frames:
                src = lookup[(resource, frame)]
                old = PRIOR / f"reference/original/{resource}/{frame:03}.png"
                raw = old.read_bytes()
                if raw != archive.read(src["path"]) or hashlib.sha256(raw).hexdigest() != src["png_sha256"]:
                    raise ValueError(f"Source mismatch: {resource} {frame:03}")
                dest = HERE / f"original/{resource}/{frame:03}.png"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(old, dest)
                with Image.open(io.BytesIO(raw)) as im:
                    mode, canvas = im.mode, list(im.size)
                    alpha = im.convert("RGBA").getchannel("A")
                    alpha_bounds = alpha.getbbox()
                code, label, detail = state(resource, frame)
                evidence = [pin(evidence_paths[0])] if resource == "SSUZY1.BMP" else []
                if resource == "SSUZY1.BMP" and frame in (0, 2):
                    evidence.append(pin(PRIOR / f"generation/{resource}/{frame:03}-v1-failure.json"))
                if resource == "SBREAKUP.BMP" and frame in (15, 16):
                    evidence.append(pin(PRIOR / f"generation/{resource}/{frame:03}-v1-attempt.json"))
                requests = [pin(p) for p in sorted((PRIOR / "generation" / resource).glob(f"{frame:03}-v*-request.json"))]
                actions = [{k:a[k] for k in ("ttm", "tag", "description", "scope")}
                    for a in resources[resource]["unique_slot_frame_actions"] if frame in a["frames"]]
                rows.append({
                    "id": f"{resource}-{frame:03}", "resource": resource, "frame": f"{frame:03}",
                    "canvas": canvas, "mode": mode, "alpha_bounds": list(alpha_bounds) if alpha_bounds else None,
                    "original": pin(dest), "url": dest.relative_to(HERE).as_posix(),
                    "prior_original": pin(old), "archive_member": src["path"],
                    "source_rgba_sha256": src["rgba_sha256"], "status": code,
                    "status_label": label, "status_detail": detail,
                    "description": DESCRIPTIONS[resource][frame],
                    "request_records": requests, "status_evidence": evidence,
                    "static_source_actions": actions
                })
    # Audit recorded JSON failures across prior art, not unretained tool history.
    matches = []
    scanned = 0
    for p in sorted((ROOT / "art/cartoon").rglob("*.json")):
        if HERE in p.parents:
            continue
        text = p.read_text(encoding="utf-8-sig")
        scanned += 1
        if re.search(r"moderation|no_image_returned|blocked", text, re.I):
            if "walk-expansion-v1" in p.parts:
                kind = "Runtime export/fit block; not an image-generation failure."
            elif "worker-tool-pose-corrections-v2" in p.parts:
                kind = "User request for this context workup; not a new failure."
            elif p == PRIOR / "batch-plan.json":
                kind = "Batch summary of deferred SSUZY1."
            else:
                kind = "Recorded image-generation failure or family status."
            matches.append({**pin(p), "interpretation": kind})
    audit = {
        "scope": "All prior art/cartoon JSON files searched for moderation, no_image_returned or blocked.",
        "json_files_scanned": scanned, "matches": matches,
        "finding": "Recorded generation blocks concern SSUZY1 and the recovered SBREAKUP015/016 pair. No other generation-block family was found in this retained JSON scan.",
        "limit": "This does not reconstruct unretained tool errors or claim that a whole deferred family was blocked."
    }
    save(HERE / "failure-record-audit.json", audit)
    # Original pixels only, nearest-neighbor enlargement and neutral display compositing.
    cell_w, cell_h = 440, 290
    sheet = Image.new("RGB", (1760, 80 + 5 * cell_h), "#edf1f4")
    draw = ImageDraw.Draw(sheet)
    font_path = Path("C:/Windows/Fonts/segoeui.ttf")
    font = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default()
    title_font = ImageFont.truetype(str(font_path), 28) if font_path.exists() else font
    draw.text((24, 18), "Original sprite context | SSUZY1 000-011 + SBREAKUP 012-018", fill="#172c3c", font=title_font)
    colors = {"blocked":"#a82920", "recovered":"#17614a", "success":"#225f87", "not-run":"#6c6077", "context":"#596b78"}
    for n, row in enumerate(rows):
        x, y = (n % 4) * cell_w, 80 + (n // 4) * cell_h
        draw.rounded_rectangle((x+8,y+6,x+432,y+282), radius=14, fill="#ffffff")
        draw.text((x+20,y+17), row["id"], fill="#172c3c", font=font)
        draw.text((x+20,y+43), row["status_label"], fill=colors[row["status"]], font=font)
        with Image.open(ROOT / row["original"]["path"]) as original:
            im = original.convert("RGBA")
            scale = max(1, min(8, 396 // im.width, 184 // im.height))
            im = im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)
            sheet.paste(im, (x+(cell_w-im.width)//2, y+83+(188-im.height)//2), im)
    sheet.save(HERE / "contact-sheet.png")
    data = {
        "schema_version": 1, "title": "Blocked originals, in context", "count": len(rows),
        "scope": "Original pixels only. Context for the user's next art-direction clarification; not a new appearance approval.",
        "palette_limit": index["palette_limit"], "archive": pin(archive_path),
        "frame_index": pin(index_path), "scene_map": pin(mapping_path),
        "rows": rows, "evidence": [pin(p) for p in evidence_paths],
        "failure_audit": pin(HERE / "failure-record-audit.json"), "contact_sheet": pin(HERE / "contact-sheet.png"),
        "source_integrity": "All19 copies equal their prior-family files and exact original-archive members. No alpha edits, recoloring, cropping or generated artwork."
    }
    save(HERE / "source.json", data)
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    payload = json.dumps(data).replace("</", "<\\/")
    (HERE / "review.html").write_text(template.replace("__DATA__", payload), encoding="utf-8")
    save(HERE / "review-record.json", {
        "schema_version": 1, "status": "context_only",
        "review": pin(HERE / "review.html"), "source": pin(HERE / "source.json"),
        "javascript": pin(HERE / "review.js"), "template": pin(HERE / "review-template.html"),
        "builder": pin(Path(__file__)), "contact_sheet": pin(HERE / "contact-sheet.png"),
        "original_count": len(rows), "generated_images_included": 0,
        "approval": None, "native_validation": False
    })
    print(json.dumps({"originals": len(rows), "statuses": {s:sum(r["status"]==s for r in rows) for s in colors},
                      "review": pin(HERE / "review.html"), "source": pin(HERE / "source.json"),
                      "audit_matches": len(matches)}, indent=2))

if __name__ == "__main__":
    main()
