"""Compare the six latest pose edits to their exact previous review versions."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / "campfire-props-direction-v2"
GROUPS = [("boots", "Boot bend", [("FIRE2.BMP", 5), ("FIRE2.BMP", 22)]),
          ("squid", "Squid face and head", [("FIRE2.BMP", n) for n in (6, 21, 24)] + [("FIRE5.BMP", 0)])]

def ident(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            alpha = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), alpha_range=list(alpha.getextrema()),
                          display_bounds=list(alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

def panel(key, kind, title, path):
    return f'<div class="panel"><h3>{title}</h3><a href="{url(path)}" target="_blank" rel="noopener" aria-label="Open {kind} {key}"><canvas width="720" height="500" data-key="{key}" data-kind="{kind}" aria-label="{title} {key}"' + (' class="pixelated"' if kind == 'original' else '') + '></canvas></a></div>'

def main():
    feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
    previous = json.loads((PREVIOUS / "review-record.json").read_text(encoding="utf-8"))
    lookup = {row["key"]: row for row in previous["rows"]}
    rows, sections, nav = [], [], []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        cards = []
        for resource, number in frames:
            key = f"{resource}{number:03}"
            folder = HERE / "generation" / resource
            record = folder / f"{number:03}-record-v1.json"
            generation = json.loads(record.read_text(encoding="utf-8"))
            request = ROOT / generation["request"]["path"]
            paths = {"original": ROOT / lookup[key]["original"]["path"],
                     "earlier": ROOT / lookup[key]["revised"]["path"],
                     "revised": folder / f"{number:03}-generated-v1.png"}
            target = feedback[group][key]
            row = {"key": key, "resource": resource, "frame": f"{number:03}", "group": group,
                   "requested_correction": target, "request": ident(request), "generation_record": ident(record)}
            for kind, path in paths.items():
                row[kind] = {**ident(path), "url": url(path)}
            rows.append(row)
            cards.append(f'<article id="{key}"><h2>{key}</h2><p class="target">{html.escape(target)}</p><div class="comparison">' +
                         ''.join(panel(key, kind, title, paths[kind]) for kind, title in [("original", "Original"), ("earlier", "Previous review"), ("revised", "New revision")]) + '</div></article>')
        sections.append(f'<section><h2 class="group" id="{group}">{title}</h2>' + '\n'.join(cards) + '</section>')
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps({"schema_version": 1, "rows": rows}, indent=2) + '\n', encoding="utf-8")
    page = (HERE / "review-template.html").read_text(encoding="utf-8").replace("{{NAV}}", ''.join(nav)).replace("{{SECTIONS}}", '\n'.join(sections))
    output = HERE / "review.html"
    output.write_text(page, encoding="utf-8")
    record = {"schema_version": 1, "date": "2026-09-18", "status": "awaiting_human_review",
              "corrected_drawings": len(rows), "visual_approval": None, "native_validation": False,
              "production_package_changed": False, "rows": rows, "page": ident(output), "data": ident(data_path),
              "helpers": [ident(HERE / p) for p in ("build_review.py", "review-template.html", "review.js")],
              "feedback": ident(HERE / "feedback.json"), "previous_review": ident(PREVIOUS / "review-record.json"),
              "user_images": [ident(p) for p in sorted((HERE / "reference/user-feedback").glob("*.png"))],
              "production_archive": ident(ROOT / "assets/scrantic_data.zip"),
              "limits": ["Drawings enlarged independently", "Native contact and motion deferred to bulk integration", "Unmentioned drawings not implicitly approved"]}
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2) + '\n', encoding="utf-8")
    print(f"Built {len(rows)} comparisons")

if __name__ == "__main__":
    main()
