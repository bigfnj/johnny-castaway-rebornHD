"""Build the 72-frame appearance gallery, including pending and failed drawings."""
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
    approval_path = HERE / "acceptance/appearance-round5-2026-09-25.json"
    approvals = json.loads(approval_path.read_text(encoding="utf-8"))["approved_assets"] if approval_path.is_file() else {}
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
            approved = approvals.get(key, {})
            if (approved.get("version") == version and row["selected_raw"]
                    and approved.get("output", {}).get("sha256") == row["selected_raw"]["sha256"]
                    and approved.get("output", {}).get("path") == row["selected_raw"]["path"]):
                message = "Appearance approved by user on September 25, 2026"
                row["status_text"] = message
                row["appearance_approval"] = pin(approval_path)
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
    output = HERE / "review-full.html"
    output.write_text(template.replace("{{NAV}}", "".join(nav)).replace("{{SECTIONS}}", "\n".join(sections)).replace("{{SUMMARY}}", html.escape(summary)), encoding="utf-8")
    helpers = ["build_review.py", "record_output.py", "review-template.html", "review.js",
               "prepare_references.py", "source-notes.md", "selection.json", "README.md",
               "merge_review_notes.py", "make_inspection_sheets.py", "audit_selection.py", "duplicate-audit.json",
               "shark-correction-overrides.json", "feedback-2026-09-24.json",
             "feedback-2026-09-24-round2.json", "review-data-before-feedback-round2.json",
             "verify_feedback_round2.py", "feedback-round2-selection-record.json",
             "browser-review-round2.json", "browser-review-round2-negative-control.json",
             "browser-review-round2.png", "feedback-2026-09-24-round3.json",
             "review-data-before-feedback-round3.json", "verify_feedback_round3.py",
             "feedback-round3-selection-record.json", "browser-review-round3.json",
             "browser-review-round3-negative-control.json", "browser-review-round3.png",
             "build_round3_review.py", "review-full.html", "review-data-round3.json",
             "review-round3-record.json", "browser-review-round3-focused.json",
             "browser-review-round3-focused-negative-control.json",
             "browser-review-round3-focused.png", "browser-review-round3-full-archive.json",
             "review-round3.html", "feedback-2026-09-24-round4.json",
             "review-data-before-feedback-round4.json", "verify_feedback_round4.py",
             "feedback-round4-selection-record.json", "build_round4_review.py",
             "validate_round4_browser.py",
             "review-data-round4.json", "review-round4-record.json",
             "browser-review-round4-focused.json",
             "browser-review-round4-focused-negative-control.json",
             "browser-review-round4-focused.png",
             "browser-review-round4-full-archive.json", "review-round4.html",
             "feedback-2026-09-24-round5.json",
             "review-data-before-feedback-round5.json", "verify_feedback_round5.py",
             "feedback-round5-selection-record.json", "build_round5_review.py",
             "validate_round5_browser.py", "review-data-round5.json",
             "review-round5-record.json", "browser-review-round5-focused.json",
             "browser-review-round5-focused-negative-control.json",
             "browser-review-round5-focused.png",
             "browser-review-round5-full-archive.json",
             "review-data-before-approval-round5.json",
             "acceptance/appearance-round5-2026-09-25.json"]
    result = {"schema_version": 1,
              "status": ("generation_in_progress" if counts.get("pending", 0) or counts.get("generated_unrecorded", 0) else "awaiting_appearance_review"),
              "selected_frame_count": len(rows), "generated_drawing_count": available,
              "counts": counts, "page": pin(output), "data": pin(data_path), "assets": rows,
              "appearance_approved_frame_count": sum(bool(row.get("appearance_approval")) for row in rows),
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
