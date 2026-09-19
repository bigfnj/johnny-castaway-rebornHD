"""Compare the two new fish shape changes with the exact prior selections."""
import hashlib
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
def rel(path): return os.path.relpath(path, HERE).replace(os.sep, "/")
feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
versions = {"000": 1, "007": 2}
titles = {"000": "000: smooth head contour", "007": "007: four compact fish"}
notes = {"000": "The bump above the eye is smoothed into a rounded contour; the actual mouth stays in place.",
         "007": "Your four-fish alternative, with short separate bodies and sunglasses on the downward-facing fish."}
rows, sections = [], []
for item in feedback["frames"]:
    f = item["frame"]
    folder = HERE / "generation/LILFISH.BMP"
    record_path = folder / f"{f}-record-v{versions[f]}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    row = {"frame": f, "version": versions[f], "record": pin(record_path),
           "request": pin(ROOT / record["request"]["path"]), "original": item["original"], "images": {}}
    cards = []
    for kind, title, path in [("earlier", "Earlier Cartoon", ROOT / item["prior_raw"]["path"]),
                              ("corrected", "New revision", folder / f"{f}-generated-v{versions[f]}.png")]:
        row["images"][kind] = {**pin(path), "url": rel(path)}
        cards.append(f'<figure><figcaption>{title}</figcaption><a class="art" href="{rel(path)}" target="_blank" rel="noopener" aria-label="Open {title} {f}"><canvas width="1000" height="620" data-frame="{f}" data-kind="{kind}" aria-label="{title} {f}"></canvas></a></figure>')
    original_url = rel(ROOT / item["original"]["path"])
    sections.append(f'<section><h2 id="frame-{f}">{titles[f]}</h2><p>{notes[f]}</p><div class="row">' + ''.join(cards) + f'</div><p class="source"><a href="{original_url}" target="_blank" rel="noopener">Open original {f}</a></p></section>')
    rows.append(row)
(HERE / "review-data.json").write_text(json.dumps({"frames": rows}, indent=2) + "\n", encoding="utf-8")
template = (HERE / "review-template.html").read_text(encoding="utf-8")
(HERE / "review.html").write_text(template.replace("{{SECTIONS}}", '\n'.join(sections)), encoding="utf-8")
review = {"schema_version": 1, "status": "awaiting_two_shape_change_review", "frames": rows,
          "page": pin(HERE / "review.html"), "data": pin(HERE / "review-data.json"), "feedback": pin(HERE / "feedback.json"),
          "helpers": [pin(HERE / p) for p in ("build_review.py", "review.js", "review-template.html")],
          "art_direction": feedback["007_count_note"], "production_archive": pin(ROOT / "assets/scrantic_data.zip"),
          "human_approval": None, "production_package_changed": False, "native_testing": False}
(HERE / "review-record.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
print("Built two shape revisions with four comparison panels")
