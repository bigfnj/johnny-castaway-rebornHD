"""Build the original / superseded dolphin / corrected shark appearance review."""
import hashlib
import html
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APPROVAL_PATH = HERE.parent / "mermaid-departures-and-dates-batch-v1" / "acceptance" / "appearance-round5-2026-09-25.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def pin(value):
    if not value:
        return None
    path = ROOT / (value["path"] if isinstance(value, dict) else value)
    if not path.is_file():
        return None
    result = {"path": path.relative_to(ROOT).as_posix(),
              "url": os.path.relpath(path, HERE).replace(os.sep, "/"),
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if isinstance(value, dict) and value.get("sha256"):
        assert value["sha256"] == result["sha256"], f"Historical file changed: {path}"
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            bounds = image.convert("RGBA").getchannel("A").point(lambda a: 255 if a >= 8 else 0).getbbox()
            assert bounds, f"Empty image: {path}"
            result.update(canvas=list(image.size), bounds=list(bounds))
    return result


def load_notes():
    notes = {}
    for path in sorted(HERE.glob("*-notes.json")):
        document = read(path)
        for key, value in document.items():
            if ".BMP-" in key and isinstance(value, str):
                notes[key] = value
        for row in document.get("assets", []):
            resource = row.get("resource", document.get("resource"))
            if resource:
                notes[f'{resource}-{str(row["frame"]).zfill(3)}'] = row.get("visual_review", row.get("source_notes", ""))
    return notes


def apply_appearance_approval(row, approval, approval_pin):
    selected = approval.get("approved_assets", {}).get(row["key"])
    if not selected or selected.get("version") != row["version"]:
        return
    expected = selected.get("output", {})
    output = row.get("output") or {}
    if not output or any(output.get(field) != expected.get(field) for field in ("path", "sha256")):
        raise ValueError(f'{row["key"]}: appearance approval does not bind selected output {output.get("path")}')
    row["appearance_approval"] = approval_pin
    row["status"] = "appearance_approved"


def main():
    plan = read(HERE / "correction-plan.json")
    notes = load_notes()
    override_path = HERE / "selected-corrections.json"
    overrides = read(override_path) if override_path.exists() else {}
    approval = read(APPROVAL_PATH) if APPROVAL_PATH.exists() else {}
    approval_pin = pin(APPROVAL_PATH.relative_to(ROOT).as_posix()) if approval else None
    rows = []
    for entry in plan["entries"]:
        row = {key: entry[key] for key in ("key", "resource", "frame", "version", "previous_version")}
        row["original"] = pin(entry["original"])
        row["previous"] = pin(entry["previous"])
        row["previous_record"] = pin(entry["previous_record"])
        assert row["original"] and row["previous"] and row["previous_record"], entry["key"]
        version = int(overrides.get(row["key"], row["version"]))
        row["version"] = version
        folder = Path(entry["output_path"]).parent
        frame = row["frame"]
        row["request"] = pin((folder / f"{frame}-v{version}-request.json").as_posix())
        row["record"] = pin((folder / f"{frame}-record-v{version}.json").as_posix())
        row["output"] = pin((folder / f"{frame}-generated-v{version}.png").as_posix()) if row["record"] else None
        row["status"] = "awaiting_review" if row["output"] else "pending"
        row["visual_review"] = notes.get(row["key"], "")
        row["appearance_approval"] = None
        apply_appearance_approval(row, approval, approval_pin)
        row["production_integrated"] = False
        row["native_motion_checked"] = False
        rows.append(row)
    counts = Counter(row["status"] for row in rows)
    assert len(rows) == 27 and len({row["key"] for row in rows}) == 27
    cards = []
    for row in rows:
        panels = []
        for kind, label in (("original", "Original pose"), ("previous", "Previous dolphin drawing"), ("output", "Corrected gray shark")):
            info = row[kind]
            content = (f'<a href="{html.escape(info["url"], quote=True)}" target="_blank"><canvas width="1000" height="650" data-key="{row["key"]}" data-kind="{kind}"></canvas></a>'
                       if info else '<div class="empty">Correction in progress</div>')
            panels.append(f'<section><h3>{label}</h3><div class="art">{content}</div></section>')
        links = " &middot; ".join(f'<a href="{html.escape(row[kind]["url"], quote=True)}" target="_blank">{label}</a>'
            for kind, label in (("request", "Exact request"), ("record", "Image record"), ("output", "Exact PNG")) if row[kind])
        if row["status"] == "appearance_approved":
            state = f'Gray shark v{row["version"]}: appearance approved on 2026-09-25'
        else:
            state = f'Gray shark v{row["version"]}: awaiting your review' if row["output"] else "Correction in progress"
        note = f'<p class="muted">{html.escape(row["visual_review"])}</p>' if row["visual_review"] else ""
        cards.append(f'<article id="frame-{row["key"]}" data-resource="{row["resource"]}" data-status="{row["status"]}"><h2>{row["resource"][:-4]} {row["frame"]}</h2><p class="state">{state}</p>{note}<div class="panels">{"".join(panels)}</div><p class="links">{links}</p></article>')
    data = {"schema_version": 1, "total": len(rows), "counts": dict(counts), "entries": rows,
            "appearance_approval": approval_pin, "production_integrated": False, "native_motion_checked": False}
    (HERE / "review-data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    summary = f'{counts.get("appearance_approved", 0)} of 27 shark corrections appearance approved; {counts.get("awaiting_review", 0)} awaiting review.'
    if counts.get("pending"):
        summary += f' {counts["pending"]} still in progress. Refresh this page for updates.'
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    page = template.replace("__SUMMARY__", summary).replace("__CARDS__", "\n".join(cards)).replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    (HERE / "review.html").write_text(page, encoding="utf-8")
    record = {"schema_version": 1, "built_at_utc": datetime.now(timezone.utc).isoformat(), "total": 27,
              "counts": dict(counts), "plan": pin("art/cartoon/shark-identity-corrections-v1/correction-plan.json"),
              "html": pin("art/cartoon/shark-identity-corrections-v1/review.html"),
              "data": pin("art/cartoon/shark-identity-corrections-v1/review-data.json"),
              "appearance_approval": approval_pin, "production_integrated": False, "native_motion_checked": False}
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": 27, "counts": dict(counts), "page": str(HERE / "review.html")}))


if __name__ == "__main__":
    main()
