"""Build the new-batch appearance gallery, including pending and failed drawings."""
import hashlib
import html
import json
import os
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = [(r.lower().replace(".bmp", ""), r.replace(".BMP", ""), r, frames) for r, frames in json.loads((HERE / "selection.json").read_text(encoding="utf-8")).items()]


def pin(path):
    value = {"path": path.relative_to(ROOT).as_posix(),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == ".png":
        with Image.open(path) as im:
            alpha = im.convert("RGBA").getchannel("A")
            bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
            value.update(canvas=list(im.size), mode=im.mode,
                         alpha_range=list(alpha.getextrema()),
                         alpha8_bounds=list(bounds) if bounds else None)
    return value


def local_url(path):
    return path.relative_to(HERE).as_posix()


def optional_pin(path):
    return pin(path) if path.is_file() else None


def main():
    plan = json.loads((HERE / "batch-plan.json").read_text(encoding="utf-8"))
    selection = json.loads((HERE / "selection.json").read_text(encoding="utf-8"))
    selected_path = HERE / "selected-versions.json"
    versions = json.loads(selected_path.read_text(encoding="utf-8")) if selected_path.exists() else {}
    notes_path = HERE / "review-notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}
    rows, nav, sections = [], [], []
    for group, title, resource, frames in GROUPS:
        frames = [n for n in frames if n in selection.get(resource, [])]
        nav.append(f'<a href="#{group}">{html.escape(title)} ({len(frames)})</a>')
        cards = []
        for n in frames:
            frame = f"{n:03}"
            key = f"{resource}-{frame}"
            version = versions.get(key, 1)
            folder = HERE / "generation" / resource
            raw = folder / f"{frame}-generated-v{version}.png"
            original = HERE / "reference/original" / resource / f"{frame}.png"
            record = folder / f"{frame}-record-v{version}.json"
            request = folder / f"{frame}-v{version}-request.json"
            failure = folder / f"{frame}-v{version}-failure.json"
            if record.is_file():
                record_data = json.loads(record.read_text(encoding="utf-8"))
                if record_data.get("request", {}).get("path"):
                    request = ROOT / record_data["request"]["path"]
            if raw.is_file():
                state = "generated" if record.is_file() else "generated_unrecorded"
                message = "Ready for appearance review" if record.is_file() else "Image returned; generation record pending"
            elif failure.is_file():
                state, message = "failed", "No image returned; see recorded failure"
            elif request.is_file():
                state, message = "pending", "Request saved; no image available yet"
            else:
                state, message = "pending", "Drawing pending"
            row = {"key": key, "resource": resource, "frame": frame, "version": version,
                   "group": group, "status": state, "status_text": message,
                   "selected_raw": optional_pin(raw), "original_reference": optional_pin(original),
                   "generation_record": optional_pin(record), "request": optional_pin(request),
                   "failure": optional_pin(failure),
                   "review_note": notes.get(key),
                   "url": local_url(raw) if raw.is_file() else None,
                   "original_url": local_url(original) if original.is_file() else None}
            rows.append(row)
            label = f"{resource.removesuffix('.BMP')} {frame}"
            review_note = f'<p class="review-note">{html.escape(notes[key])}</p>' if key in notes else ""
            links = []
            for path, text in [(request, "Exact saved request"), (record, "Generation record"),
                               (failure, "Recorded failure")]:
                if path.is_file():
                    # Request records may refer to files in a sibling batch.
                    href = os.path.relpath(path, HERE).replace("\\", "/")
                    links.append(f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">{text}</a>')
            if raw.is_file():
                cartoon = (f'<a class="art" href="{row["url"]}" target="_blank" rel="noopener" aria-label="Open cartoon {key}">'
                           f'<canvas width="720" height="440" data-key="{key}" data-kind="cartoon" aria-label="Cartoon {key}"></canvas></a>')
            else:
                cartoon = f'<div class="missing {state}"><p>{message}</p><span>The exact original remains available below.</span></div>'
            if original.is_file():
                source = (f'<a class="original" href="{row["original_url"]}" target="_blank" rel="noopener">'
                          f'<canvas width="720" height="250" data-key="{key}" data-kind="original" aria-label="Original {key}"></canvas></a>')
            else:
                source = '<p class="missing-original">Original reference unavailable</p>'
            cards.append(f'<figure id="{key}" data-filter="{html.escape(key + " " + title + " " + state)}">'
                         f'<figcaption>{label}<span>{html.escape(title)}</span></figcaption>'
                         f'<p class="state {state}">{message}</p>{review_note}{cartoon}'
                         f'<p class="links">{" &middot; ".join(links) if links else "Request not yet saved"}</p>'
                         f'<details open><summary>Original {key}</summary>{source}</details></figure>')
        sections.append(f'<section><h2 id="{group}">{html.escape(title)}</h2><div class="grid">' + "\n".join(cards) + "</div></section>")
    expected = {(r, f"{n:03}") for r, frames in selection.items() for n in frames}
    observed = {(r["resource"], r["frame"]) for r in rows}
    if len(rows) != plan["target_new_drawings"] or observed != expected:
        raise ValueError("Gallery groups must cover every selected frame exactly once")
    counts = dict(Counter(r["status"] for r in rows))
    available = sum(r["selected_raw"] is not None for r in rows)
    summary = (f'{available} images available; {counts.get("pending", 0)} pending; '
               f'{counts.get("failed", 0)} failed. {len(rows)} original comparisons.')
    data_path = HERE / "review-data.json"
    data_path.write_text(json.dumps({"assets": rows, "counts": counts, "summary": summary}, indent=2) + "\n", encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    output = HERE / "review.html"
    output.write_text(template.replace("{{TITLE}}", html.escape(plan.get("title", "Next Cartoon scenes"))).replace("{{NAV}}", "".join(nav)).replace("{{SECTIONS}}", "\n".join(sections)).replace("{{SUMMARY}}", html.escape(summary)), encoding="utf-8")
    helpers = ["build_review.py", "record_output.py", "review-template.html", "review.js",
               "prepare_references.py", "source-notes.md", "selection.json", "README.md"]
    result = {"schema_version": 1,
              "status": ("generation_in_progress" if counts.get("pending", 0) or counts.get("generated_unrecorded", 0) else "generation_incomplete" if counts.get("failed", 0) else "awaiting_appearance_review"),
              "selected_frame_count": len(rows), "generated_drawing_count": available,
              "counts": counts, "page": pin(output), "data": pin(data_path), "assets": rows,
              "source_record": pin(HERE / "reference/source.json"), "batch_plan": pin(HERE / "batch-plan.json"),
              "helpers": [pin(HERE / name) for name in helpers if (HERE / name).is_file()],
              "visual_approval": None, "production_acceptance": False, "native_validation": False,
              "production_package_changed": False, "production_archive": pin(ROOT / "assets/scrantic_data.zip"),
              "deferred_work": ["Original canvas placement and multipart registration", "Native sequence and motion checks", "Bulk smoke and regression tests"]}
    if selected_path.exists():
        result["selected_versions"] = pin(selected_path)
    if notes_path.exists():
        result["review_notes"] = pin(notes_path)
    (HERE / "review-record.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(rows)} comparisons across {len(GROUPS)} sections. {summary}")


if __name__ == "__main__":
    main()
