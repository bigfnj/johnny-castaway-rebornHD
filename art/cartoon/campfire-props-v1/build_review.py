"""Build the 25-drawing prop gallery without changing generated image bytes."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERSIONS = {("FIRE2.BMP", 9): 3, ("FIRE2.BMP", 15): 3}
GROUPS = [
    ("fish", "Fish and the separate tail", [("FIRE2.BMP", n) for n in (1, 2, 12, 13, 14, 17, 18, 20)] + [("FIRE5.BMP", 2)]),
    ("boots", "Old boots and the separate toe", [("FIRE2.BMP", n) for n in (4, 5, 9, 15, 16, 19, 22, 23)] + [("FIRE5.BMP", 1)]),
    ("squid", "Squid poses", [("FIRE2.BMP", n) for n in (6, 7, 21, 24)] + [("FIRE5.BMP", 0)]),
    ("raft", "Raft and paddle", [("SRAFT.BMP", n) for n in (0, 1)]),
]

def ident(path):
    result = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            a = im.convert("RGBA").getchannel("A")
            result.update(canvas=list(im.size), mode=im.mode, alpha_range=list(a.getextrema()),
                          alpha_bounds=list(a.getbbox()), alpha8_bounds=list(a.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return result

def url(path):
    return os.path.relpath(path, HERE).replace(os.sep, "/")

def label(resource, n, group):
    if resource == "SRAFT.BMP":
        return "Log raft" if n == 0 else "Wooden paddle"
    if resource == "FIRE5.BMP":
        return "Companion source variant"
    return {18: "Separate tail", 19: "Separate toe / sole", 21: "Curled eating pose", 24: "Curled eating pose"}.get(n, {"fish": "Fish pose", "boots": "Boot pose", "squid": "Squid pose"}[group])

def main():
    assets, sections, nav = [], [], []
    for group, title, frames in GROUPS:
        cards = []
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        for resource, n in frames:
            frame = f"{n:03}"
            folder = HERE / "generation" / resource
            version = VERSIONS.get((resource, n), 1)
            raw = folder / f"{frame}-generated-v{version}.png"
            original = HERE / "reference/original" / resource / f"{frame}.png"
            record = folder / f"{frame}-record-v{version}.json"
            generation = json.loads(record.read_text(encoding="utf-8"))
            request = ROOT / (generation["request"]["path"] if "request" in generation else generation["request_path"])
            # Resolve every selected asset before publishing a new page or manifest.
            row = {"resource": resource, "frame": frame, "version": version, "group": group, "kind": "generated_draft",
                   "selected_raw": ident(raw), "original_reference": ident(original), "request": ident(request), "generation_record": ident(record)}
            if row["selected_raw"]["alpha_range"] != [0, 255]:
                raise ValueError(f"Missing transparent/opaque range: {raw}")
            row["url"] = url(raw)
            row["original_url"] = url(original)
            assets.append(row)
            name = label(resource, n, group)
            key = f"{resource}-{frame}"
            note = "Source variant; scene usage still unconfirmed." if resource == "FIRE5.BMP" else "This is a separate piece, not a complete prop." if n in (18, 19) and resource == "FIRE2.BMP" else ""
            cards.append(f'''<figure id="{key}"><figcaption>{html.escape(name)}<span>{key}</span></figcaption>
<a class="art" href="{url(raw)}" target="_blank" rel="noopener" aria-label="Open full drawing {key}"><canvas width="720" height="420" data-key="{key}" aria-label="Cartoon {key}"></canvas></a>
<small>{note or 'Click the drawing to open its full image.'}</small><details><summary>Compare original {key}</summary><div class="original"><img src="{url(original)}" alt="Original {key}"></div></details></figure>''')
        sections.append(f'<section><h2 id="{group}">{title}</h2><div class="grid">'+"\n".join(cards)+"</div></section>")
    preserved, deferred = [], []
    for n in (0, 3, 8):
        p = HERE / f"source-preserved/FIRE2.BMP/{n:03}.png"
        original = HERE / f"reference/original/FIRE2.BMP/{n:03}.png"
        if p.read_bytes() != original.read_bytes():
            raise ValueError(f"Source-preserved bytes differ: {p}")
        preserved.append({"resource": "FIRE2.BMP", "frame": f"{n:03}", "kind": "source_preserved", "file": ident(p)})
    for n in (10, 11):
        deferred.append({"resource": "FIRE2.BMP", "frame": f"{n:03}", "kind": "deferred_character_grip_overlay", "original_reference": ident(HERE / f"reference/original/FIRE2.BMP/{n:03}.png")})
    data = {"schema_version": 1, "assets": assets, "preserved": preserved, "deferred": deferred}
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    page = template.replace("{{NAV}}", "".join(nav)).replace("{{SECTIONS}}", "\n".join(sections))
    output = HERE / "review.html"
    output.write_text(page, encoding="utf-8")
    record = {"schema_version": 1, "status": "awaiting_batch_appearance_review", "date": "2026-09-18",
              "generated_drawing_count": len(assets), "preserved_source_slot_count": 3, "deferred_character_overlay_count": 2, "total_source_slots": 30,
              "reviewed_url": "http://127.0.0.1:8941/campfire-props-v1/review.html", "page": ident(output), "data": ident(data_path),
              "helpers": [ident(HERE / p) for p in ("build_review.py", "review-template.html", "review.js")],
              "source_record": ident(HERE / "reference/source.json"), "assets": assets, "preserved": preserved, "deferred": deferred,
              "visual_approval": None, "production_acceptance": False, "production_package_changed": False,
              "production_archive": ident(ROOT / "assets/scrantic_data.zip"), "export_executed": False,
              "deferred_work": ["Original-canvas fitting and registration", "Johnny hand/mouth joins and cooking/eating composites", "FIRE5 scene-usage attribution", "SRAFT scene/paddle joins", "Native smoke and bulk regressions"]}
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(f"Gallery: {len(assets)} drawings; 3 exact markers; 2 deferred grips")

if __name__ == "__main__":
    main()
