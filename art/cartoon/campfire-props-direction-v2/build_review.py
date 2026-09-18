"""Present pose corrections beside the original and rejected earlier interpretation."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EARLIER = HERE.parent / "campfire-props-v1"
VERSIONS = {("FIRE2.BMP", n): 2 for n in (12, 13, 14)}
GROUPS = [("fish", "Upside-down fish", [("FIRE2.BMP", n) for n in (12, 13, 14)]),
          ("boots", "Boot orientation and fragments", [("FIRE2.BMP", n) for n in (5, 9, 15, 19, 22)]),
          ("squid", "Squid eyes and gaze", [("FIRE2.BMP", n) for n in (6, 7, 21, 24)] + [("FIRE5.BMP", 0)])]

def ident(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), alpha_range=list(a.getextrema()),
                          display_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

def panel(key, kind, title, path, pixelated=False):
    return f'''<div class="panel"><h3>{title}</h3><a href="{url(path)}" target="_blank" rel="noopener" aria-label="Open {kind} {key}"><canvas width="720" height="500" data-key="{key}" data-kind="{kind}" aria-label="{title} {key}"{' class="pixelated"' if pixelated else ''}></canvas></a></div>'''

def main():
    feedback = json.loads((HERE / "feedback.json").read_text(encoding="utf-8"))
    previous = json.loads((EARLIER / "review-record.json").read_text(encoding="utf-8"))
    lookup = {(r["resource"], int(r["frame"])): r for r in previous["assets"]}
    rows, sections, nav = [], [], []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        cards = []
        for resource, n in frames:
            key = f"{resource}{n:03}"
            version = VERSIONS.get((resource, n), 1)
            folder = HERE / "generation" / resource
            revised = folder / f"{n:03}-generated-v{version}.png"
            record = folder / f"{n:03}-record-v{version}.json"
            generation = json.loads(record.read_text(encoding="utf-8"))
            request = ROOT / (generation["request"]["path"] if "request" in generation else generation["request_path"])
            old = lookup[(resource, n)]
            original = ROOT / old["original_reference"]["path"]
            earlier = ROOT / old["selected_raw"]["path"]
            target = feedback[group][key]
            display_target = "Upside-down boot piece: sole above, toe at the left and the short connection below the right end." if key == "FIRE2.BMP019" else target
            row = {"key": key, "resource": resource, "frame": f"{n:03}", "group": group, "version": version, "requested_correction": target,
                   "request": ident(request), "generation_record": ident(record)}
            for kind, path in [("original", original), ("earlier", earlier), ("revised", revised)]:
                row[kind] = {**ident(path), "url": url(path)}
            rows.append(row)
            cards.append(f'<article id="{key}"><h2>{key}</h2><p class="target">{html.escape(display_target)}</p><div class="comparison">'+
                         panel(key, "original", "Original", original, True)+panel(key, "earlier", "Earlier Cartoon", earlier)+panel(key, "revised", "Revised Cartoon", revised)+"</div></article>")
        sections.append(f'<section><h2 class="group" id="{group}">{title}</h2>'+"\n".join(cards)+"</section>")
    changed = {(r["resource"], int(r["frame"])) for r in rows}
    unchanged = [r for r in previous["assets"] if (r["resource"], int(r["frame"])) not in changed]
    data = {"schema_version": 1, "rows": rows, "unchanged": unchanged}
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    page = (HERE / "review-template.html").read_text(encoding="utf-8").replace("{{NAV}}", "".join(nav)).replace("{{SECTIONS}}", "\n".join(sections))
    output = HERE / "review.html"
    output.write_text(page, encoding="utf-8")
    record = {"schema_version": 1, "status": "awaiting_human_pose_correction_review", "date": "2026-09-18", "corrected_drawings": len(rows),
              "unchanged_drawings": len(unchanged), "visual_approval": None, "production_package_changed": False, "native_validation": False,
              "review_url": "http://127.0.0.1:8941/campfire-props-direction-v2/review.html", "page": ident(output), "data": ident(data_path), "rows": rows,
              "helpers": [ident(HERE / p) for p in ("build_review.py", "review-template.html", "review.js")],
              "feedback": ident(HERE / "feedback.json"), "user_images": [ident(p) for p in sorted((HERE / "reference/user-feedback").glob("*.png"))],
              "earlier_review_record": ident(EARLIER / "review-record.json"), "boot019_context": ident(HERE / "reference/boot019-scene-context.json"),
              "production_archive": ident(ROOT / "assets/scrantic_data.zip"),
              "limits": ["Still pose review; no native motion", "Original diagnostic palette", "Other twelve drawings retained, not implicitly approved", "Hand/mouth joins and full-canvas registration deferred"]}
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(f"Built {len(rows)} revised comparisons; {len(unchanged)} earlier drawings unchanged")

if __name__ == "__main__":
    main()
