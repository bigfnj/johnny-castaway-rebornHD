"""Build the focused review from the four correction manifests and 005 selection."""
import hashlib
import html
import json
import os
from collections import Counter
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLDERS = ("suzy", "gift014", "preserver", "glimse", "selection005")
FRIENDLY = {"SSUZY1.BMP": "Suzy", "SMGIFT.BMP": "Mermaid gifts", "SMGLIMSE.BMP": "Mermaid glimpses"}

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def pin(value):
    if not value:
        return None
    raw = value["path"] if isinstance(value, dict) else value
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        return None
    result = {"path": path.relative_to(ROOT).as_posix(), "url": os.path.relpath(path, HERE).replace(os.sep, "/"),
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if isinstance(value, dict) and value.get("sha256"):
        assert value["sha256"] == result["sha256"], raw
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            alpha = image.convert("RGBA").getchannel("A")
            result.update(canvas=list(image.size), bounds=list(alpha.point(lambda a:255 if a >= 8 else 0).getbbox()))
    return result

def load_entries():
    rows = read(HERE / "review-scope.json")["entries"]
    by_key = {(row["resource"], str(row["frame"]).zfill(3)): row for row in rows}
    for folder in FOLDERS:
        path = HERE / folder / "manifest.json"
        if not path.exists():
            continue
        manifest = read(path)
        for entry in manifest["entries"]:
            key = (entry["resource"], str(entry["frame"]).zfill(3))
            assert key in by_key, key
            by_key[key].update(entry)
            by_key[key]["manifest"] = pin(path)
    for row in rows:
        row["frame"] = str(row["frame"]).zfill(3)
        row["key"] = f'{row["resource"]}-{row["frame"]}'
        row["title"] = f'{FRIENDLY[row["resource"]]} {row["frame"]}'
        for kind in ("original", "previous", "output", "request", "record", "latest_attempt_request", "latest_attempt_record"):
            row[kind] = pin(row.get(kind))
        row.setdefault("appearance_approval", None)
        row["production_integrated"] = False
        row["native_motion_checked"] = False
        if row["output"] and row["status"] not in ("selected_by_user", "approved_by_user", "needs_correction"):
            row["status"] = "awaiting_review"
    return rows

def main():
    rows = load_entries()
    counts = Counter(row["status"] for row in rows)
    cards = []
    for row in rows:
        selected = row["status"] == "selected_by_user"
        status = "Selected by you; restored unchanged" if selected else "New correction: awaiting your review" if row["output"] else "Correction in progress" if row["status"] == "pending" else "No revised image returned"
        if row["status"] == "needs_correction":
            status = "Incomplete draft: mouth detail missing; repair returned no image"
        if row["status"] == "approved_by_user":
            status = "Appearance approved by you"
        panels = []
        for kind, title in (("original", "Original"), ("previous", "Previous drawing"), ("output", row.get("output_label") or ("Approved correction" if row["status"] == "approved_by_user" else "New candidate"))):
            image = row[kind]
            content = (f'<a href="{html.escape(image["url"], quote=True)}" target="_blank"><canvas width="1000" height="650" data-key="{row["key"]}" data-kind="{kind}"></canvas></a>' if image else '<div class="empty">No new image yet</div>')
            panels.append(f'<section><h3>{html.escape(title)}</h3><div class="art">{content}</div></section>')
        links = " &middot; ".join(f'<a href="{html.escape(row[k]["url"], quote=True)}" target="_blank">{label}</a>' for k,label in (("request","Exact request"),("record","Image record"),("output","Exact PNG"),("latest_attempt_request","Latest repair request"),("latest_attempt_record","Latest repair outcome")) if row.get(k))
        note = f'<p class="muted">{html.escape(row["visual_review"])}</p>' if row.get("visual_review") else ""
        cards.append(f'<article id="frame-{row["key"]}" data-resource="{row["resource"]}"><h2>{row["title"]}</h2><p class="state">{status}</p><p>{html.escape(row["requested_change"])}</p>{note}<div class="panels">{"".join(panels)}</div><p class="links">{links}</p></article>')
    data = {"schema_version": 1, "total": len(rows), "counts": dict(counts), "entries": rows,
            "production_integrated": False, "native_motion_checked": False}
    (HERE / "review-data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    summary = f'{counts.get("approved_by_user",0)} corrections approved; {counts.get("awaiting_review",0)} new candidates awaiting review. 005 remains your selected partial v2.'
    if counts.get("no_image"):
        summary += f' {counts["no_image"]} requested correction has no new image.'
    if counts.get("needs_correction"):
        summary += f' {counts["needs_correction"]} draft still needs correction.'
    page = PAGE.replace("__SUMMARY__", summary).replace("__CARDS__", "\n".join(cards)).replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    (HERE / "review.html").write_text(page, encoding="utf-8")
    print(json.dumps({"total": len(rows), "counts": dict(counts), "page": str(HERE / "review.html")}))

PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Requested art corrections</title>
<style>:root{color-scheme:dark;--bg:#142730;--card:#223f4d;--ink:#f1f7fa;--muted:#bed6df;--check1:#f4f1e8;--check2:#dfdacd}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}header,main{max-width:1700px;margin:auto;padding:22px}h1{margin:0;font-size:28px}h2{margin:0;font-size:22px}h3{font-size:15px;margin:0 0 8px}a{color:#a7e7fa}p{margin:9px 0}.muted,.links{color:var(--muted);font-size:14px}.tools{position:sticky;top:0;z-index:5;background:#142730ef;padding:12px 22px;border-block:1px solid #52707d;display:flex;gap:14px;align-items:center}select,button{font:inherit;background:#294b5b;border:1px solid #87a5b0;color:var(--ink);border-radius:6px;padding:8px 12px;cursor:pointer}article{background:var(--card);padding:20px;border-radius:12px;margin-bottom:20px;scroll-margin-top:85px}.state{color:#a6eac3;font-weight:600}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:16px}.art{aspect-ratio:1000/650;background-color:var(--check1);background-image:conic-gradient(var(--check2) 25%,transparent 0 50%,var(--check2) 0 75%,transparent 0);background-size:24px 24px;border-radius:5px;overflow:hidden}.art a,canvas{display:block;width:100%;height:100%}.empty{height:100%;display:grid;place-items:center;color:#49545b}.dark{--check1:#36454f;--check2:#26333d}.dark .empty{color:#d0dee4}[hidden]{display:none!important}nav{display:flex;gap:16px;flex-wrap:wrap}@media(max-width:850px){.panels{grid-template-columns:1fr}header,main{padding:14px}.tools{flex-wrap:wrap}}</style></head><body>
<header><h1>Requested art corrections</h1><p>__SUMMARY__</p><p class="muted">Compare each original, previous drawing, and new correction. New drawings await your appearance review.</p><nav><a href="../visitor-leg-pose-corrections-v2/color-sequence-review.html">Suzy sequence</a><a href="../visitor-leg-pose-corrections-v2/review.html">Visitor review history</a><a href="../mermaid-expression-corrections-v1/review.html">Mermaid review history</a></nav></header>
<div class="tools"><label>Show <select id="resource"><option value="">All requested corrections</option><option value="SSUZY1.BMP">Suzy</option><option value="SMGIFT.BMP">Mermaid gifts</option><option value="SMGLIMSE.BMP">Mermaid glimpses</option></select></label><button id="checker">Use dark checkerboard</button><span id="loading" class="muted">Loading drawing panels...</span></div><main>__CARDS__</main>
<script id="review-data" type="application/json">__DATA__</script><script>
'use strict';const data=JSON.parse(document.getElementById('review-data').textContent),tasks=data.entries.flatMap(row=>['original','previous','output'].filter(kind=>row[kind]).map(kind=>({row,kind,info:row[kind]})));let loaded=0,errors=0;
document.getElementById('resource').onchange=event=>{for(const card of document.querySelectorAll('article'))card.hidden=Boolean(event.target.value&&card.dataset.resource!==event.target.value)};
document.getElementById('checker').onclick=event=>{const dark=document.body.classList.toggle('dark');event.target.textContent=dark?'Use light checkerboard':'Use dark checkerboard'};
async function worker(){while(tasks.length){const{row,kind,info}=tasks.shift(),canvas=document.querySelector('canvas[data-key="'+row.key+'"][data-kind="'+kind+'"]');try{const image=new Image();image.src=info.url+'?sha='+info.sha256;await image.decode();const b=info.bounds,w=b[2]-b[0],h=b[3]-b[1],scale=Math.min((canvas.width-40)/w,(canvas.height-40)/h),ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=kind!=='original';ctx.drawImage(image,(canvas.width-w*scale)/2-b[0]*scale,(canvas.height-h*scale)/2-b[1]*scale,image.width*scale,image.height*scale);canvas.dataset.loaded='true';loaded++}catch(error){errors++;canvas.dataset.loaded='false';canvas.after(document.createTextNode('Image could not load: '+error.message))}document.getElementById('loading').textContent=loaded+' drawing panels loaded'+(errors?'; '+errors+' errors':'')}}
Promise.all(Array.from({length:5},worker)).then(()=>{document.getElementById('loading').dataset.complete='true'});
</script></body></html>'''

if __name__ == "__main__":
    main()
