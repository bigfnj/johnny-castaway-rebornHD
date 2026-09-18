"""Show two boot angle edits beside the original and the user's actual cutout."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / "campfire-props-bend-v3"
VERSIONS = {"005": 2, "022": 2}

def ident(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), alpha_range=list(a.getextrema()),
                          display_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

def main():
    feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
    previous = json.loads((PREVIOUS / "review-record.json").read_text(encoding="utf-8"))
    lookup = {r["frame"]: r for r in previous["rows"] if r["resource"] == "FIRE2.BMP"}
    cards, rows = [], []
    for n, info in feedback["frames"].items():
        key = "FIRE2.BMP" + n
        folder = HERE / "generation/FIRE2.BMP"
        version = VERSIONS[n]
        record_path = folder / f"{n}-record-v{version}.json"
        generation = json.loads(record_path.read_text(encoding="utf-8"))
        request = ROOT / generation["request"]["path"]
        paths = {"original": ROOT / lookup[n]["original"]["path"],
                 "target": HERE / "reference/user-feedback" / info["annotation"],
                 "revised": folder / f"{n}-generated-v{version}.png"}
        row = {"key": key, "resource": "FIRE2.BMP", "frame": n, "version": version, "request": ident(request),
               "generation_record": ident(record_path), "requested_correction": info["target"],
               "previous_draft": lookup[n]["revised"]}
        panels = []
        for kind, title in [("original", "Original"), ("target", "Your pose reference"), ("revised", "New revision")]:
            path = paths[kind]
            row[kind] = {**ident(path), "url": url(path)}
            if kind == "target":
                row[kind]["source_rect"] = info["display_crop"]
            panels.append(f'<div class="panel"><h3>{title}</h3><a href="{url(path)}" target="_blank" rel="noopener" aria-label="Open {kind} {key}"><canvas width="720" height="600" data-key="{key}" data-kind="{kind}" aria-label="{title} {key}"></canvas></a></div>')
        rows.append(row)
        cards.append(f'<article id="{key}"><h2>{key}</h2><p>{html.escape(info["target"])}</p><div class="comparison">' + ''.join(panels) + '</div></article>')
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps({"rows": rows}, indent=2) + '\n', encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    output = HERE / "review.html"
    output.write_text(template.replace("{{CARDS}}", '\n'.join(cards)), encoding="utf-8")
    review = {"schema_version": 1, "status": "awaiting_human_review", "visual_approval": None,
              "corrected_drawings": len(rows), "rows": rows, "page": ident(output), "data": ident(data_path),
              "helpers": [ident(HERE / p) for p in ("build_review.py", "review-template.html", "review.js")],
              "feedback": ident(HERE / "feedback.json"), "previous_review": ident(PREVIOUS / "review-record.json"),
              "production_archive": ident(ROOT / "assets/scrantic_data.zip"), "production_package_changed": False,
              "native_validation": False,
              "limits": ["Reference panel is a browser-only crop of the unmodified user screenshot", "All drawings independently enlarged", "Scene fitting and native testing deferred to bulk integration"]}
    (HERE / "review-record.json").write_text(json.dumps(review, indent=2) + '\n', encoding="utf-8")
    print(f"Built {len(rows)} boot comparisons")

if __name__ == "__main__":
    main()
