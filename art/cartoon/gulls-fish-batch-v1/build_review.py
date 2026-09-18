"""Build one review of the complete42-slot gull/nest and small-fish families."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = [
    ("flight", "Gull flight and dives", [("GJGULL1.BMP", n) for n in list(range(8)) + [25, 26]]),
    ("standing", "Gull landing, turns and pecking", [("GJGULL1.BMP", n) for n in range(8, 25)]),
    ("nests", "Nest construction, sitting gull and egg", [("GJGULL1.BMP", n) for n in range(27, 33)]),
    ("fish", "Small fish, separate tails and catch groups", [("LILFISH.BMP", n) for n in range(9)]),
]

def ident(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), mode=im.mode, alpha_range=list(a.getextrema()),
                          alpha8_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

def label(resource, n):
    if resource == "LILFISH.BMP":
        return {0: "Upright fish", 1: "Upright fish", 2: "Fish body / head component", 3: "Separate tail", 4: "Separate tail", 5: "Single fish", 6: "Two-fish catch", 7: "Three-fish catch", 8: "Four-fish catch"}[n]
    if n < 8: return "Flight pose"
    if n == 8: return "Landing pose"
    if n < 25: return "Standing / turning / pecking pose"
    return {25: "Head-first dive", 26: "Opposite head-first dive", 27: "Initial nest sticks", 28: "Partial nest", 29: "Building nest", 30: "Complete nest", 31: "Gull sitting in nest", 32: "Egg in nest"}[n]

def main():
    selections = json.loads((HERE / "selected-versions.json").read_text(encoding="utf-8")) if (HERE / "selected-versions.json").exists() else {}
    rows, sections, nav = [], [], []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        cards = []
        for resource, n in frames:
            frame = f"{n:03}"
            key = f"{resource}-{frame}"
            version = selections.get(key, 1)
            folder = HERE / "generation" / resource
            raw = folder / f"{frame}-generated-v{version}.png"
            original = HERE / "reference/original" / resource / f"{frame}.png"
            record = folder / f"{frame}-record-v{version}.json"
            generation = json.loads(record.read_text(encoding="utf-8"))
            request = ROOT / generation["request"]["path"]
            row = {"key": key, "resource": resource, "frame": frame, "version": version, "group": group,
                   "label": label(resource, n), "selected_raw": ident(raw), "original_reference": ident(original),
                   "generation_record": ident(record), "request": ident(request)}
            row["url"], row["original_url"] = url(raw), url(original)
            rows.append(row)
            note = "Separate component: keep its original assembly role." if resource == "LILFISH.BMP" and n in (2, 3, 4) else "Keep the fish count and overlaps shown in the original." if resource == "LILFISH.BMP" and n >= 6 else ""
            cards.append(f'<figure data-filter="{html.escape(key + " " + title + " " + row["label"])}"><figcaption>{html.escape(row["label"])}<span>{key}</span></figcaption>'
                         f'<a class="art" href="{url(raw)}" target="_blank" rel="noopener" aria-label="Open Cartoon {key}"><canvas width="720" height="460" data-key="{key}" data-kind="cartoon" aria-label="Cartoon {key}"></canvas></a>'
                         f'<small>{note or "Click the drawing for the full image."}</small><details open><summary>Original {key}</summary>'
                         f'<a class="original" href="{url(original)}" target="_blank" rel="noopener"><canvas width="720" height="240" data-key="{key}" data-kind="original" aria-label="Original {key}"></canvas></a></details></figure>')
        sections.append(f'<section><h2 id="{group}">{title}</h2><div class="grid">' + '\n'.join(cards) + '</div></section>')
    data = HERE / "review-data.json"
    data.write_text(json.dumps({"assets": rows}, indent=2) + '\n', encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    output = HERE / "review.html"
    output.write_text(template.replace("{{NAV}}", ''.join(nav)).replace("{{SECTIONS}}", '\n'.join(sections)), encoding="utf-8")
    review = {"schema_version": 1, "status": "awaiting_42_drawing_appearance_review", "generated_drawing_count": len(rows),
              "page": ident(output), "data": ident(data), "assets": rows, "source_record": ident(HERE / "reference/source.json"),
              "batch_plan": ident(HERE / "batch-plan.json"), "selection_research": ident(HERE / "reference/selection-research.json"),
              "helpers": [ident(HERE / p) for p in ("build_review.py", "review-template.html", "review.js")],
              "visual_approval": None, "production_acceptance": False, "native_validation": False,
              "production_package_changed": False, "production_archive": ident(ROOT / "assets/scrantic_data.zip"),
              "deferred_work": ["Original canvas fit and shadow/ground contact", "Complete native action order and layering", "Bulk smoke/regression and delivery audit"]}
    if (HERE / "selected-versions.json").exists(): review["selected_versions"] = ident(HERE / "selected-versions.json")
    (HERE / "review-record.json").write_text(json.dumps(review, indent=2) + '\n', encoding="utf-8")
    print(f"Built {len(rows)} drawings in {len(GROUPS)} groups")

if __name__ == "__main__":
    main()
