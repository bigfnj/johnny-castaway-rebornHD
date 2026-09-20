"""Build the 67-drawing visitor and thought-scene gallery with visible originals."""
import hashlib
import html
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = json.loads((HERE / 'gallery-groups.json').read_text(encoding='utf-8'))

def pin(path):
    value = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == ".png":
        with Image.open(path) as im:
            alpha = im.convert("RGBA").getchannel("A")
            value.update(canvas=list(im.size), mode=im.mode, alpha_range=list(alpha.getextrema()),
                         alpha8_bounds=list(alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return value

def main():
    selections_path = HERE / "selected-versions.json"
    selections = json.loads(selections_path.read_text(encoding="utf-8")) if selections_path.exists() else {}
    rows, nav, sections = [], [], []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        cards = []
        for resource, n in frames:
            frame = f"{n:03}"
            key = f"{resource}-{frame}"
            version = selections.get(key, 1)
            raw = HERE / f"generation/{resource}/{frame}-generated-v{version}.png"
            original = HERE / f"reference/original/{resource}/{frame}.png"
            record = HERE / f"generation/{resource}/{frame}-record-v{version}.json"
            request = ROOT / json.loads(record.read_text(encoding="utf-8"))["request"]["path"]
            row = {"key": key, "resource": resource, "frame": frame, "version": version, "group": group,
                   "selected_raw": pin(raw), "original_reference": pin(original),
                   "generation_record": pin(record), "request": pin(request),
                   "url": raw.relative_to(HERE).as_posix(), "original_url": original.relative_to(HERE).as_posix()}
            rows.append(row)
            label = f"{resource.removesuffix('.BMP')} {frame}"
            cards.append(f'<figure id="{key}" data-filter="{html.escape(key + " " + title)}"><figcaption>{label}<span>{title}</span></figcaption>'
                         f'<a class="art" href="{row["url"]}" target="_blank" rel="noopener" aria-label="Open Cartoon {key}"><canvas width="720" height="440" data-key="{key}" data-kind="cartoon" aria-label="Cartoon {key}"></canvas></a>'
                         f'<details open><summary>Original {key}</summary><a class="original" href="{row["original_url"]}" target="_blank" rel="noopener"><canvas width="720" height="250" data-key="{key}" data-kind="original" aria-label="Original {key}"></canvas></a></details></figure>')
        sections.append(f'<section><h2 id="{group}">{title}</h2><div class="grid">' + "\n".join(cards) + "</div></section>")
    assert len(rows) == 67 and len({r["key"] for r in rows}) == 67
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps({"assets": rows}, indent=2) + "\n", encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    output = HERE / "review.html"
    output.write_text(template.replace("{{NAV}}", "".join(nav)).replace("{{SECTIONS}}", "\n".join(sections)), encoding="utf-8")
    record = {"schema_version": 1, "status": "awaiting_67_drawing_appearance_review", "generated_drawing_count": len(rows),
              "page": pin(output), "data": pin(data_path), "assets": rows,
              "source_record": pin(HERE / "reference/source.json"), "batch_plan": pin(HERE / "batch-plan.json"),
              "helpers": [pin(HERE / n) for n in ("build_review.py", "record_output.py", "review-template.html", "review.js", "gallery-groups.json", "prepare_references.py", "source-notes.md", "selection.json")],
              "visual_approval": None, "production_acceptance": False, "native_validation": False,
              "production_package_changed": False, "production_archive": pin(ROOT / "assets/scrantic_data.zip"),
              "deferred_work": ["Original canvas placement and multipart registration", "Native sequence and motion checks", "Bulk smoke and regression tests"]}
    if selections_path.exists(): record["selected_versions"] = pin(selections_path)
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(rows)} drawings across {len(GROUPS)} sections")

if __name__ == "__main__":
    main()
