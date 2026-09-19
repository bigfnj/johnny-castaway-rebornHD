"""Build ten user-directed corrections with original/earlier/corrected panels."""
import hashlib
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def pin(path):
    item = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            item.update(canvas=list(im.size), alpha_range=list(a.getextrema()),
                        alpha8_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return item

def rel(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
versions = json.loads((HERE / "selected-versions.json").read_text(encoding="utf-8"))
notes = {item['frame']:item['correction'] for item in feedback['frames']}
rows, sections = [], []
for item in feedback["frames"]:
    f = item["frame"]
    version = versions[f]
    folder = HERE / "generation/GJGULL2.BMP"
    record_path = folder / f"{f}-record-v{version}.json"
    generation = json.loads(record_path.read_text(encoding="utf-8"))
    row = {"frame": f, "version": version, "record": pin(record_path),
           "request": pin(ROOT / generation["request"]["path"]), "images": {}}
    cards = []
    for kind, title, path in [
        ("original", "Original", ROOT / item["original"]["path"]),
        ("earlier", "Earlier Cartoon", ROOT / item["prior_raw"]["path"]),
        ("corrected", "Corrected Cartoon", folder / f"{f}-generated-v{version}.png"),
    ]:
        row["images"][kind] = {**pin(path), "url": rel(path)}
        cards.append(f'<figure><figcaption>{title}</figcaption><a class="art" href="{rel(path)}" target="_blank" rel="noopener" aria-label="Open {title} {f}"><canvas width="960" height="600" data-frame="{f}" data-kind="{kind}" aria-label="{title} {f}"></canvas></a></figure>')
    sections.append(f'<section><h2 id="frame-{f}">GJGULL2 {f}</h2><p>{notes[f]}</p><div class="row">' + "".join(cards) + "</div></section>")
    rows.append(row)
(HERE / "review-data.json").write_text(json.dumps({"frames": rows}, indent=2) + "\n", encoding="utf-8")
template = (HERE / "review-template.html").read_text(encoding="utf-8")
(HERE / "review.html").write_text(template.replace("{{SECTIONS}}", "\n".join(sections)), encoding="utf-8")
review = {"schema_version": 1, "status": "awaiting_ten_gull_clothes_stick_corrections_review", "frames": rows,
          "page": pin(HERE / "review.html"), "data": pin(HERE / "review-data.json"), "feedback": pin(HERE / "feedback.json"),
          "helpers": [pin(HERE / p) for p in ("build_review.py", "review.js", "review-template.html", "record_output.py", "prepare_feedback.py")],
          "selected_versions": pin(HERE / "selected-versions.json"),
          "production_archive": pin(ROOT / "assets/scrantic_data.zip"),
          "human_approval": None, "production_package_changed": False, "native_testing": False}
(HERE / "review-record.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
assert len(rows) == 10
print("Built ten corrections with thirty comparison panels")
