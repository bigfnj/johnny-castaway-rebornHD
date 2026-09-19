"""Build the five requested fish corrections beside their original and prior art."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def pin(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), alpha_range=list(a.getextrema()),
                          alpha8_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def rel(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
selection_path = HERE / "selected-versions.json"
versions = json.loads(selection_path.read_text(encoding="utf-8")) if selection_path.exists() else {}
rows, sections = [], []
for item in feedback["frames"]:
    frame = item["frame"]
    version = versions.get(frame, 1)
    folder = HERE / "generation/LILFISH.BMP"
    record_path = folder / f"{frame}-record-v{version}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    paths = {"original": ROOT / item["original"]["path"], "earlier": ROOT / item["prior_raw"]["path"],
             "corrected": folder / f"{frame}-generated-v{version}.png"}
    row = {"frame": frame, "version": version, "user_note": item["user_note"],
           "record": pin(record_path), "request": pin(ROOT / record["request"]["path"]), "images": {}}
    cards = []
    for kind, title in (("original", "Original"), ("earlier", "Earlier Cartoon"), ("corrected", "Corrected Cartoon")):
        path = paths[kind]
        row["images"][kind] = {**pin(path), "url": rel(path)}
        cards.append(f'<figure><figcaption>{title}</figcaption><a class="art" href="{rel(path)}" target="_blank" rel="noopener" aria-label="Open {title} {frame}"><canvas width="900" height="540" data-frame="{frame}" data-kind="{kind}" aria-label="{title} {frame}"></canvas></a></figure>')
    sections.append(f'<section><h2 id="frame-{frame}">LILFISH.BMP-{frame}</h2><p>{html.escape(item["user_note"])}</p><div class="row">' + ''.join(cards) + '</div></section>')
    rows.append(row)
(HERE / "review-data.json").write_text(json.dumps({"frames": rows}, indent=2) + "\n", encoding="utf-8")
template = (HERE / "review-template.html").read_text(encoding="utf-8")
nav = ''.join(f'<a href="#frame-{r["frame"]}">{r["frame"]}</a>' for r in rows)
(HERE / "review.html").write_text(template.replace("{{NAV}}", nav).replace("{{SECTIONS}}", '\n'.join(sections)), encoding="utf-8")
review = {"schema_version": 1, "status": "awaiting_five_fish_appearance_review", "frames": rows,
          "page": pin(HERE / "review.html"), "data": pin(HERE / "review-data.json"), "feedback": pin(HERE / "feedback.json"),
          "helpers": [pin(HERE / p) for p in ("build_review.py", "review.js", "review-template.html")],
          "production_archive": pin(ROOT / "assets/scrantic_data.zip"), "production_package_changed": False,
          "human_approval": None, "native_testing": False}
if selection_path.exists():
    review["selected_versions"] = pin(selection_path)
(HERE / "review-record.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
print("Built five fish corrections with 15 comparison panels")
